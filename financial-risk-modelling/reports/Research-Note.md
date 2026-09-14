# Market risk: does model complexity improve loss coverage?
Historical study prepared September 2026. Dataset ends December 2018.

## Decision and result
A risk manager needs to know whether a forecast covers tail losses and whether misses cluster. All three methods reject joint conditional coverage at 5% in this fixed historical backtest. None is ready for a production risk limit merely because its calculations run.

| Method | Confidence | Exceptions / 4,030 | Expected | Kupiec p | Conditional coverage p |
| --- | --- | --- | --- | --- | --- |
| GARCH-t 1000d | 95% | 243 | 201.5 | 0.003619 | 0.01184 |
| GARCH-t 1000d | 99% | 63 | 40.3 | 0.0008994 | 0.002658 |
| Historical 250d | 95% | 210 | 201.5 | 0.5416 | 5.136e-05 |
| Historical 250d | 99% | 55 | 40.3 | 0.02745 | 0.01188 |
| Normal 1000d | 95% | 196 | 201.5 | 0.6897 | 1.324e-05 |
| Normal 1000d | 99% | 94 | 40.3 | 4.191e-13 | 4.491e-18 |

At 99%, historical VaR has 55 exceptions, GARCH-t 63 and the normal model 94, against 40.3 expected. GARCH-t improves on the normal model, but does not beat the simple historical method on exception count. Coverage and independence should be considered together; a non-rejection would not prove validity. The tests are asymptotic and overlapping rolling estimates can affect inference.

## Method
Daily return = 100 × log(P_t/P_(t−1)); loss is its negative. Positive values mean losses. Every VaR and ES is in **percent log-return loss**, not arithmetic return or pounds. Confidence levels 95% and 99%; one trading-day horizon. No annualisation or square-root-of-time conversion.

Forecasts cover 2002-12-27–2018-12-31, 4,030 days. Historical VaR/ES use the preceding 250 returns. Normal mean and standard deviation use the preceding 1,000. GARCH(1,1) with constant mean and unit-variance Student-t innovations uses 1,000 returns, refits every 63 trading days and updates conditional variance each intervening day. These are declared benchmark choices, not parameters optimised on backtest success. Unequal windows mean the comparison concerns whole specifications, not just distribution choice.

For each forecast dated t, estimation ends t−1. Fit failure stops the run. GARCH recurrence is checked against the arch library's one-step forecast. Historical ES integrates the empirical quantile tail, including fractional boundary mass. Parametric Student-t ES uses the analytical tail mean; tests compare it with numerical integration.

Kupiec tests unconditional exception frequency. Christoffersen transition likelihood tests exception independence; their likelihood-ratio sum tests conditional coverage. Empty transition rows are reported as unidentified rather than a spurious perfect pass. Binomial coverage intervals are supplied as descriptive iid intervals. `mean_tail_residual` is the average realised loss minus forecast ES on VaR-exception days: a descriptive severity diagnostic, **not a formal ES calibration test**.

## Monte Carlo and its limits
100,000 seeded paths simulate ten trading days with recursively evolving GARCH variance and Student-t innovations. Parameters are estimated from the last 1,000 returns at 31 December 2018. The 99% simulated ten-day VaR is 16.34% and ES 23.04% in log-loss units. These are historical, conditional scenario outputs, not present-day risk estimates. Ten-day simulated outputs are not independently backtested here.

The final alpha + beta is approximately 1.000: the fit is at the persistence boundary. It does not provide a finite long-run unconditional variance. Finite-horizon simulation remains defined, but long-horizon stability claims would be unjustified. Student-t innovations are symmetric, while equity drawdowns may be asymmetric. Parameter uncertainty and Monte Carlo sampling error are not incorporated in a confidence interval.

## Next validation priorities
1. Predeclare a development/validation/test regime for improving specifications; the existing backtest is now observed and must not become an unlabelled fresh holdout.
2. Compare GJR-GARCH or filtered historical simulation on new data, including COVID-19; add regime-specific results and formal joint VaR/ES scoring or calibration.
3. Investigate persistence at the boundary; add parameter uncertainty and bootstrap uncertainty for model comparisons.
4. For a lending bank, build a separate borrower credit-risk study. Market VaR is not PD/LGD/EAD, impairment or affordability modelling.

## Sources and reproducibility
[arch model documentation](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_modeling.html) and [forecast documentation](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_forecasting.html). Input provenance and redistribution status are in `data/README.md`. `daily_backtest.csv`, `garch_refits.csv` and `results.json` expose every estimate and evaluation output.
