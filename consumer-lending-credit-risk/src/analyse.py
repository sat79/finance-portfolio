"""Synthetic consumer lending: grade PD calibration, affordability and loss stress.

Python 3.10+, standard library only. Not a deployable lending decision system.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def payment(principal, annual_rate, months):
    if not all(math.isfinite(v) for v in (principal, annual_rate, months)):
        raise ValueError('Inputs must be finite')
    if principal <= 0 or annual_rate < 0 or months <= 0 or int(months) != months:
        raise ValueError('Invalid loan terms')
    r = annual_rate / 12
    return principal / months if r == 0 else principal * r / (-math.expm1(-months * math.log1p(r)))


def expected_loss(pd, lgd, ead):
    if not all(math.isfinite(x) for x in (pd, lgd, ead)) or not 0 <= pd <= 1 or not 0 <= lgd <= 1 or ead < 0:
        raise ValueError('Invalid PD, LGD or EAD')
    return pd * lgd * ead


def first_year_cashflows(loan):
    balance = loan['principal']
    instalment = payment(balance, loan['annual_rate'], loan['term_months'])
    interest = 0.0
    exposure_sum = 0.0
    for _ in range(min(12, loan['term_months'])):
        exposure_sum += balance
        interest_month = balance * loan['annual_rate'] / 12
        interest += interest_month
        balance = max(0.0, balance + interest_month - instalment)
    return interest, exposure_sum / 12


def grade(loan):
    # Fixed before fitting; only application-time fields are used.
    points = (loan['utilisation'] >= 0.65) + (loan['utilisation'] >= 0.85) + 2 * (loan['prior_arrears'] > 0)
    return 'ABCD'[min(points, 3)]


def fit_pd(train):
    buckets = defaultdict(list)
    for loan in train:
        buckets[grade(loan)].append(loan['default_12m'])
    # Beta(1,19) smoothing; an explicit 5% prior, not an industry benchmark.
    return {g: (sum(buckets[g]) + 1) / (len(buckets[g]) + 20) for g in 'ABCD'}


def affordable(loan, stressed=False):
    income = loan['net_monthly_income'] * (0.9 if stressed else 1)
    spending = loan['essential_spending'] * (1.1 if stressed else 1)
    residual = income - spending - loan['existing_debt_payment'] - payment(loan['principal'], loan['annual_rate'], loan['term_months'])
    return residual >= (100 if stressed else 250)


def evaluate(loans, pds, cutoff, stress=False):
    selected = [x for x in loans if pds[grade(x)] <= cutoff and affordable(x) and affordable(x, True)]
    el = margin = principal = 0.0
    for loan in selected:
        pd = min(1, pds[grade(loan)] * (1.7 if stress else 1))
        lgd = 0.65 if stress else 0.5
        loss = expected_loss(pd, lgd, loan['principal'])
        interest, average_balance = first_year_cashflows(loan)
        # Conservative initial-principal EAD. Performing interest proxy is reduced
        # by PD; no default-time cashflow model, capital charge or acquisition cost.
        margin += (1 - pd) * interest - average_balance * (0.07 if stress else 0.05) - 120 - loss
        el += loss
        principal += loan['principal']
    return {'applications': len(loans), 'approved': len(selected), 'approval_rate': len(selected) / len(loans) if loans else 0,
            'principal_gbp': principal, 'expected_loss_gbp': el, 'expected_contribution_gbp': margin,
            'observed_default_rate': sum(x['default_12m'] for x in selected) / len(selected) if selected else None}


def auc(labels, scores):
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        return None
    # Pairwise definition handles tied grade scores explicitly.
    return sum((a > b) + 0.5 * (a == b) for y, a in zip(labels, scores) if y
               for z, b in zip(labels, scores) if not z) / (positives * negatives)


def load_data(path):
    rows = []
    with path.open(newline='') as f:
        for raw in csv.DictReader(f):
            x = {k: (v if k == 'loan_id' else float(v)) for k, v in raw.items()}
            for k in ['vintage_year', 'term_months', 'prior_arrears', 'default_12m']:
                if not x[k].is_integer():
                    raise ValueError('Integer field contains a fraction')
                x[k] = int(x[k])
            if not all(math.isfinite(v) for k, v in x.items() if k != 'loan_id'):
                raise ValueError('Nonfinite data')
            if x['default_12m'] not in (0, 1) or not 0 <= x['utilisation'] <= 1 or x['prior_arrears'] < 0:
                raise ValueError('Invalid outcome or risk field')
            if x['vintage_year'] not in (2022, 2023, 2024) or x['net_monthly_income'] <= 0 or min(x['essential_spending'], x['existing_debt_payment']) < 0:
                raise ValueError('Invalid vintage or affordability field')
            payment(x['principal'], x['annual_rate'], x['term_months'])
            rows.append(x)
    if len({x['loan_id'] for x in rows}) != len(rows):
        raise ValueError('Duplicate loan IDs')
    if {x['vintage_year'] for x in rows} != {2022, 2023, 2024}:
        raise ValueError('All three chronological cohorts are required')
    return rows


def run(data_path, output):
    loans = load_data(data_path)
    train, validation, test = [[x for x in loans if x['vintage_year'] == yr] for yr in (2022, 2023, 2024)]
    pds = fit_pd(train)
    candidates = {str(c): evaluate(validation, pds, c) for c in (0.0, 0.03, 0.06, 0.10, 0.15, 1.0)}
    cutoff = float(max(candidates, key=lambda c: candidates[c]['expected_contribution_gbp']))
    labels = [x['default_12m'] for x in test]
    scores = [pds[grade(x)] for x in test]
    baseline = (sum(x['default_12m'] for x in train) + 1) / (len(train) + 20)
    calibration = []
    for g in 'ABCD':
        cohort = [x for x in test if grade(x) == g]
        calibration.append({'grade': g, 'count': len(cohort), 'estimated_pd': pds[g],
                            'observed_default_rate': sum(x['default_12m'] for x in cohort) / len(cohort) if cohort else None})
    result = {'data_status': 'Entirely synthetic; no customer or employer data',
              'split': {'train_year': 2022, 'validation_year': 2023, 'test_year': 2024},
              'grade_pd': pds, 'selected_pd_cutoff': cutoff, 'validation_candidates': candidates,
              'test_brier': sum((p-y)**2 for p,y in zip(scores, labels)) / len(test),
              'constant_baseline_brier': sum((baseline-y)**2 for y in labels) / len(test),
              'test_auc': auc(labels, scores), 'test_calibration': calibration,
              'test_base': evaluate(test, pds, cutoff), 'test_stress_same_book': evaluate(test, pds, cutoff, True)}
    output.mkdir(parents=True, exist_ok=True)
    (output/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    with (output/'calibration.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(calibration[0]));writer.writeheader();writer.writerows(calibration)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'data/synthetic_applications.csv')
    parser.add_argument('--output', type=Path, default=ROOT/'reports')
    args = parser.parse_args()
    run(args.data, args.output)
