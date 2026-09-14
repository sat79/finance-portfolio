# Data and assumptions

Source: the included `src/generate_data.py`, seed 79014. Created 14 September 2026. All observations are invented, with 600 applications in each illustrative vintage. No customer, Zopa or Novuna data are used.

| Field | Definition |
|---|---|
| loan_id | Unique synthetic application identifier |
| vintage_year | Cohort label: 2022 training, 2023 policy selection, 2024 final test |
| net_monthly_income | Monthly disposable income before the listed outgoings, GBP |
| essential_spending | Essential monthly living costs, GBP |
| existing_debt_payment | Existing monthly contractual debt payments, GBP |
| principal | Proposed new loan amount, GBP |
| annual_rate | Nominal annual interest rate as a decimal; divided by 12 for monthly amortisation; no fees |
| term_months | Contractual duration in months |
| utilisation | Illustrative revolving-credit utilisation, from 0 to 1 |
| prior_arrears | Application-time indicator of previous arrears, 0 or 1 |
| default_12m | Synthetic default indicator within 12 months; outcome only, never an input to grading |

All cohort outcomes are assumed mature. The synthetic grade default probabilities are 2.5%, 5.5%, 11% and 20%, multiplied by 1.0, 1.1 and 1.35 in successive vintages. The true generator probabilities are not passed to the PD estimator. Income, spending, rates and loan sizes are invented distributions, not market estimates.

Base affordability requires at least £250 monthly residual income. The stressed check requires £100 after income falls 10% and essential costs rise 10%. These are illustrative policy choices, not statutory thresholds or an employer's criteria.

First-year contribution uses scheduled interest × (1 − PD), less funding cost on average monthly opening balances, £120 servicing cost and PD × LGD × initial principal. It excludes acquisition cost, capital, tax, recoveries beyond LGD, default timing and prepayment. It is a deliberately simple screening proxy, not accounting profit.
