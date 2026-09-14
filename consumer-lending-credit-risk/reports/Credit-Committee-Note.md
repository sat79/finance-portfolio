# Credit committee note
14 September 2026 · Independent synthetic consumer-lending study

## Decision

Keep the selected policy under review and prioritise PD recalibration. The later cohort exhibits materially higher default rates in the grades selected for lending. The model's positive contribution estimate is conditional on PD and cost assumptions that require more scrutiny.

## Evidence

| Metric | Test base | Stress on the same book |
|---|---:|---:|
| Applications | 600 | 600 |
| Approved applications | 327 | 327 |
| Principal | £3,115,000 | £3,115,000 |
| Expected loss proxy | £29,107 | £64,327 |
| Expected first-year contribution | £142,050 | £46,766 |

Test-period AUC is 0.674 and Brier score is 0.05527, versus 0.05673 for a constant training-PD benchmark. The small Brier improvement must be read alongside calibration. Grade A estimates 1.56% defaults versus 3.37% observed; grade B estimates 2.78% versus 7.76% observed. The selected synthetic borrowers have a 3.98% observed default rate. This is not directly comparable with an exposure-weighted expected-loss rate.

The PD cutoff is 3%; cutoffs of 6% and 10% select the same grades and book. The lowest cutoff wins this tie. The policy is selected on 2023 expected contribution with PDs estimated exclusively from 2022, then held fixed for 2024. The final test period is not used to tune the cutoff.

## Business interpretation

Affordability and credit risk answer different questions. A borrower can satisfy residual-income rules while remaining credit-risky. Applying both checks is more useful than presenting a single score as a complete decision.

The stress scenario increases loss and funding costs without changing the selected book. Its purpose is to show sensitivity, not forecast a recession. The observed default rate remains unchanged in the stress output because historical synthetic outcomes are not rewritten.

Before progressing beyond a portfolio demonstration, obtain consented or appropriately licensed data with precise definitions, model default timing and amortising exposure, validate affordability inputs, assess calibration and subgroup outcomes, include capital/acquisition costs, and establish independent model review. No real borrower decisions should use this simulation.

## Recruiter discussion

This project connects portfolio risk monitoring, consumer affordability and lending economics. It is intended to support interviews for junior credit, forecasting and finance roles at consumer lenders. It does not reproduce Zopa's or Novuna's internal policies or systems.
