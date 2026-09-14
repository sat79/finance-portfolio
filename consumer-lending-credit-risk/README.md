# Consumer lending: credit risk and portfolio economics

**Question:** How does a lender balance approval volumes, affordability, expected losses and contribution when credit conditions deteriorate?

A consumer-finance case study for discussions with bank and fintech recruiters, including teams at Zopa and Novuna. Independent portfolio work, with no affiliation or employer data.

**All 1,800 applications and default outcomes are synthetic.** This demonstrates a reproducible analytical method; the results are not evidence of performance on real borrowers.

[Credit committee note](reports/Credit-Committee-Note.md) · [Results](reports/results.json) · [Data dictionary](data/README.md) · [Calculation tests](tests/test_credit.py)

## Key findings in this simulation

- The policy selects grades A/B, accepting 327 of 600 test applications (54.5%) after base and stressed affordability checks.
- On £3.115m of simulated lending, the one-year expected loss proxy rises from £29,107 to £64,327 under stress. Contribution falls from £142,050 to £46,766 before acquisition costs and capital charges.
- Test AUC is 0.674. Grade PDs materially understate later observed defaults in A/B: ranking alone is not sufficient evidence that a credit model is safe to use.
- The recommendation is to investigate calibration drift and full unit economics before considering any expansion. A larger approval rate is not automatically better lending.

## Reproduce

Python 3.10+; standard library only. From this directory:

```bash
python3 -m unittest discover -s tests -v
python3 src/analyse.py
```

The included CSV is frozen. `python3 src/generate_data.py` regenerates it with seed 79014. `python3 src/analyse.py --output /tmp/credit-results` preserves the distributed report. No credentials, downloads or APIs are needed.

## Method

1. Fixed grade rules use application-time utilisation and prior arrears only.
2. Calibrate grade PDs on 2022 outcomes using explicit Beta(1,19) smoothing.
3. On the 2023 cohort, choose among fixed PD cutoffs by expected contribution after affordability filters. Include a decline-all alternative and prefer the lowest cutoff in a tie. This uses model estimates, not realised validation profit, and does not prove optimality.
4. Freeze the policy and evaluate once on the 2024 cohort. Report whole-cohort discrimination, Brier score, calibration and accepted-book outcomes.
5. Stress the same accepted book: PD ×1.7, LGD 50% → 65%, annual funding cost 5% → 7%.

`src/` owns calculations and data generation; `tests/` checks financial identities, invalid inputs, leakage controls and stress direction; `data/` contains inputs and provenance; `reports/` contains conclusions and outputs.

## Limitations

The generator explicitly links default probability to the same grade features. Predictive results are therefore partly built into the simulation. The cohorts are illustrative and fully matured over a synthetic 12-month window; there is no censoring or reject inference. No protected characteristics are used, and no fairness conclusion can be drawn without an appropriate assessment. The expected loss is a simple one-year PD × LGD × initial principal proxy, not IFRS 9 ECL. Nominal annual interest rates exclude fees and are not quoted regulatory APRs. No live credit decision, customer suitability or regulatory-compliance claim is made.
