"""Generate synthetic applicants; no empirical calibration or real customer data."""
import csv
import random
from pathlib import Path


def generate(path):
    rng = random.Random(79014)
    rows = []
    for year in (2022, 2023, 2024):
        for i in range(600):
            income = round(rng.uniform(1600, 5200), 2)
            utilisation = round(rng.betavariate(2, 2), 4)
            arrears = int(rng.random() < 0.12)
            score = min(3, int(utilisation >= .65) + int(utilisation >= .85) + 2 * arrears)
            latent_pd = [0.025, 0.055, 0.11, 0.20][score] * {2022: 1, 2023: 1.1, 2024: 1.35}[year]
            row = {'loan_id': f'SYN-{year}-{i:04}', 'vintage_year': year,
                   'net_monthly_income': income, 'essential_spending': round(income*rng.uniform(.35,.65),2),
                   'existing_debt_payment': round(income*rng.uniform(.04,.25),2),
                   'principal': rng.choice([4000, 6000, 10000, 15000, 20000]),
                   'annual_rate': round(rng.uniform(.08,.18),4), 'term_months': rng.choice([24,36,48,60]),
                   'utilisation': utilisation, 'prior_arrears': arrears,
                   'default_12m': int(rng.random() < latent_pd)}
            rows.append(row)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1]/'data/synthetic_applications.csv')
