# Satvik Sahni | Finance Research Portfolio

**MSc Finance, University of Bath · Valuation · Credit risk · Forecasting · Financial analysis**

I use financial analysis to test assumptions, understand business performance and explain what the evidence means for a decision. This repository contains six complete, downloadable studies with source files, data, reports and calculation tests.

[GitHub profile](https://github.com/sat79) · [LinkedIn](https://www.linkedin.com/in/satviksahnifinance/)

## Start here

| Project | Financial question | Evidence |
|---|---|---|
| [Consumer lending and credit risk](consumer-lending-credit-risk/) | How do affordability, credit losses and funding costs affect lending economics? | Synthetic applications, chronological evaluation, PD calibration, stress and committee note |
| [Kaspi.kz valuation and bank risk](kspi-valuation-bank-risk/) | How do payout, FX and lending economics affect shareholder value? | [Excel model](kspi-valuation-bank-risk/models/KSPI-Valuation-and-Bank-Risk.xlsx), dividend scenarios, segment SQL and geographic earnings bridge |
| [Unilever equity valuation](unilever-equity-valuation/) | Which operating and discount-rate assumptions drive value? | [Excel model](unilever-equity-valuation/models/Unilever-Valuation-Reviewed.xlsx), DCF, residual income and sensitivities |
| [Financial risk modelling](financial-risk-modelling/) | Do risk forecasts cover losses that actually occur? | Historical/normal VaR, ES, GARCH-t and backtesting |
| [Time-series econometrics](time-series-econometrics/) | Does multivariate information improve historical GDP forecasts? | ARIMA, VAR/VECM and chronological validation |
| [AURA and blockchain microfinance](blockchain-microfinance-aura/) | When does technical efficiency translate into inclusion? | Dissertation-derived framework, scoring audit and adoption scenarios |

## What to inspect

Every project exposes `src/`, `data/`, `tests/` and `reports/`. KSPI and Unilever also contain editable workbooks in `models/`. Open a project README for its question, findings, exact run commands and limitations. Download everything with GitHub's **Code → Download ZIP**, or clone:

```bash
git clone https://github.com/sat79/finance-portfolio.git
cd finance-portfolio
python3 scripts/check_portfolio.py
```

The check runner uses Python 3.10+ and checks the standard-library projects, workbook calculations and all project manifests. To run the numerical studies, install their pinned dependencies as described in their READMEs. Market data for the risk study are reconstructed from the documented dependency rather than redistributed as an unlicensed raw download.

## Financial judgment and scope

- **Credit:** all borrower records and outcomes are synthetic. Calibration deterioration matters despite positive modelled contribution.
- **KSPI:** baseline scenario values are $73.11 / $45.53 / $95.68 per ADS for Base / Downside / Upside. These are assumptions-based outputs, not live price targets.
- **Unilever:** a retrospective FY2024 study with 98 independently reproduced saved formula values. Native Excel recalculation is a separate check.
- **Risk:** the historical backtests reject nominal coverage. A passing calculation test does not rescue a weak risk forecast.
- **Econometrics:** revised historical data carry hindsight. No real-time forecasting claim is made.
- **AURA:** a conceptual framework with a quantitative audit; empirical validation remains outstanding.

Reported data, analyst assumptions and new portfolio extensions are distinguished within the studies. None of the work is a production bank system or a current investment recommendation. See [verification scope](reports/Verification.md).

## About me

My experience spans mortgage valuation operations at Better.com and budgeting, pricing, inventory and P&L responsibility as Founder & Manager of Café On The Go, bringing a long-held family business idea to life. I am targeting Financial Analyst, Risk, Corporate Finance, Investment Banking and fintech opportunities.

**Tools:** Excel · Python · SQL · MATLAB
