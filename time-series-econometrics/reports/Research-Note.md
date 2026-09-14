# Economic forecasting: benchmark before adding complexity
Historical US study prepared September 2026. This is a revised-data exercise, not a real-time forecasting claim.

## Decision and result
Can multivariate information improve the next quarter's GDP-growth forecast over a simple historical average?

| Split | Model | Quarters | RMSE (pp) | MAE (pp) | 95% interval coverage |
| --- | --- | --- | --- | --- | --- |
| test | ARIMA | 39 | 2.659 | 1.962 | 94.9% |
| test | Historical mean | 39 | 3.130 | 2.184 | Not estimated |
| test | Random walk | 39 | 3.184 | 2.655 | Not estimated |
| test | VAR | 39 | 2.376 | 1.785 | 97.4% |
| test | VECM | 39 | 2.376 | 1.785 | 97.4% |
| validation | ARIMA | 40 | 1.961 | 1.532 | 100.0% |
| validation | Historical mean | 40 | 2.179 | 1.607 | Not estimated |
| validation | Random walk | 40 | 3.917 | 3.540 | Not estimated |
| validation | VAR | 40 | 1.892 | 1.446 | 100.0% |
| validation | VECM | 40 | 1.892 | 1.446 | 100.0% |

The validation-selected model is **VAR**. VECM has rank zero, so it reduces to the same VAR in first differences. Their numerical equality is expected; it is not two independent confirmations. A declared 1e−8 RMSE tie tolerance chooses the simpler labelled VAR. Reported final test results do not determine model selection.

## Design
- Training: 1959Q1–1989Q4. Only this period chooses the specification.
- Validation: 1990Q1–1999Q4, 40 expanding-window one-step forecasts. This period selects the model class by RMSE.
- Final historical test: 2000Q1–2009Q3, 39 expanding-window forecasts. Parameters may be re-estimated using observations available up to the preceding quarter, while lag orders and cointegration rank remain fixed.
- Target: 400 × log(GDP_t/GDP_(t−1)), annualised log growth in percent. This is not the exact compounded annualised growth rate. Error units are percentage points.

ADF and KPSS are applied to log levels with constant and trend, and first differences with a constant, using training data. They have opposite null hypotheses. KPSS boundary p-values are bounds, with warnings retained in results.json. GDP and consumption are consistent with I(1) in this training sample. Investment rejects the ADF trend unit-root null and does not reject KPSS trend stationarity, so it is excluded from the I(1) system instead of forcing all variables into VECM.

ARIMA (2, 1, 0) is selected by training AIC from five declared candidates, with drift. Models are estimated on percentage log levels to improve numerical conditioning; forecasts are converted back to the declared target. Optimiser failure stops the run.

The two-variable VAR uses 1 lag of GDP and consumption log differences, selected by training BIC from 1–4 lags (a zero suggestion is floored at one for the declared dynamic comparison). Johansen trace testing at 5%, an unrestricted constant and no deterministic trend select rank 0. **This sample does not support a nonzero cointegrating relationship under this specification.** No long-run equilibrium or causal relationship is claimed.

95% model intervals are conditional Gaussian forecast intervals; parameter uncertainty, publication lags and data revisions are not included. Historical-mean and random-walk intervals are deliberately not manufactured. ARIMA residual Ljung–Box p = 0.456 at eight lags, with ARMA degrees-of-freedom adjustment, is a limited serial-correlation check, not complete validation.

## What a banker should take from it
Forecast errors and uncertainty should accompany a planning assumption. Even when a multivariate model improves average error, it can miss a recession. These US macro results cannot be treated as a UK loan-loss forecast without estimating the link to a suitable lending portfolio.

## Remaining improvements
Use UK GDP, unemployment and rates with actual release vintages and publication calendars. Add rolling error stability, structural-break checks, multi-quarter horizons, multivariate residual diagnostics and interval recalibration. Test a nonzero-rank VECM only where diagnostics support it; do not manufacture cointegration to satisfy a methods list. A larger fresh holdout is needed before claiming stable relative performance.

[Dataset source and public-domain statement](https://www.statsmodels.org/stable/datasets/generated/macrodata.html). `forecasts.csv` exposes quarter, fit cutoff, prediction, observed outcome, interval and split. `model_comparison.csv` contains the full scorecard.
