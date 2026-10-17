# Your first FinSight walkthrough

## What you are learning

- A **schema** defines valid inputs: dates, currencies, financial metric names and provenance. Pydantic enforces it before calculations.
- A **pure function** produces an answer from its inputs without calling an API or changing a file. These functions make financial arithmetic easy to test independently.
- **Provenance** is the chain from a result back to the input observation, concept, period and original disclosure. A source URL alone is not enough to establish that a number matches it.
- A **fixture** is frozen test input. Our small fixture is fictional and deliberately labelled; its purpose is reproducible edge-case tests.
- **Mocking** replaces a network response during a test. It checks our handling of that response; it does not prove SEC access or financial authenticity.

## Inspect the work

On GitHub, select branch `feat/finsight-research-mvp` and open this project. Start with `src/finsight/financials.py`, then `models.py`, `selection.py`, and their tests. `app/main.py` presents the results. Existing workbook/credit projects have not been folded into the new app.

## Run the verified offline workflow

1. Follow README installation commands and start Streamlit.
2. Choose **Synthetic example** and click **Load fictional example**. Note the explicit fictional-data warning and June fiscal year-ends.
3. Open **Financial statements**. FY2023 revenue is 1,200 USD, operating profit 96 USD, CFO −20 USD, and PP&E purchases 30 USD. These are teaching numbers.
4. Open **Ratios & trends**. Independently check: `(1,200 / 1,000 − 1) × 100 = 20%` growth; `96 / 1,200 × 100 = 8%` operating margin; `−20 − 30 = −50` cash-flow proxy. Margin declined from 10% to 8%, a **2 percentage-point** change.
5. Open **Sources & warnings**. Inspect status, period, input source reference and observation ID. There is no invented SEC filing URL for the fictional data.
6. Open **Export**, download the CSV bundle or XLSX and inspect financials, calculations, sources, warnings and metadata. Match a calculation's `input_ids` to source `fact_id`s. Numeric columns are exact decimal strings; convert chosen columns to numbers in Excel when doing arithmetic there.
7. Switch to **Upload CSV**, select `data/examples/valid_synthetic.csv`, inspect the preview and click **Analyse validated CSV**. This import is labelled user-provided. Try `invalid_negative_capex.csv`; it must explain the positive-outflow convention and reject the file.

## Analyse a real company when SEC access is enabled

1. Configure `SEC_USER_AGENT` with your real contact email in the local shell, then restart the app.
2. Choose **SEC company → KSPI** (the default); AAPL and MSFT are also available, then **Fetch SEC annual data**.
3. If an error appears, read it; an empty analysis is preferable to pretending the example is live. Ensure the environment permits the official SEC destinations.
4. Once retrieval succeeds, review at least three annual periods. In Sources, trace one selected revenue observation via the SEC filing index to the actual annual statement (20-F for KSPI; 10-K for AAPL/MSFT). Confirm the amount, period, concept, filing date and unit scaling.
5. Compare that source amount with the exported financial observation. Verify a ratio independently with a calculator. Investigate any competing-value or mixed-filing warning before interpreting the result.
6. Fill the manual reconciliation register with the exact filing reference and your independently read number. A successful download alone does not complete this step.

The development check retrieved three KSPI periods and five each for AAPL/MSFT, and reconciled 48 figures across three years per company. Follow these steps yourself; source validation remains an analyst responsibility.

## Your exercise — not completed for you

Add one unit test in `tests/test_financials.py` showing that a company with a 15 USD operating loss and 200 USD revenue has a negative operating margin. Before running the code, write the expected result by hand. Use `Decimal`, call `margin_percent`, and assert the result.

Then explain: why is a loss valid, but a zero revenue denominator unsuitable for this ratio? Record your answer in `LEARNING_LOG.md`. Do not mark the exercise complete until you have run and explained it yourself.

Interview checkpoint: explain the difference between a passing arithmetic test, a mocked API test and reconciliation against an authentic filing. Explain why FY, calendar year and the `fy` metadata on a comparative disclosure are not interchangeable.

## Colab option

Keep Lesson 01's existing Colab workflow. For the new calculation layer in a Python 3.12 Colab runtime, clone the repo, switch to the feature branch, enter this project and run `%pip install -r requirements.txt`. Then import `Decimal` and `finsight.financials.margin_percent`, and run tests with `!python -m pytest -q`. These Colab steps are guidance, not a claim of executed Colab validation. Use your Mac for the Streamlit browser workflow; no paid hosting or tunnel is required.

## Your KSPI checkpoint

In FY2025, confirm consolidated revenue of KZT4,046,074 million against the 20-F. The older portfolio study uses segment revenue of KZT4,101,961 million before customer rewards. Explain the KZT55,887 million difference using the [KSPI methodology](kspi-methodology.md), then explain why the app suppresses a simple FCF proxy for a financial group. This exercise is **not completed for you**.
