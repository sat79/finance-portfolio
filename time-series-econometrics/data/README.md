# Dataset and provenance
`us_macro.csv` contains all 203 quarterly rows and 14 variables from `statsmodels.datasets.macrodata`, 1959Q1–2009Q3. Extracted from statsmodels 0.15.0 on 12 September 2026, without subsequent live refresh.

The dataset was compiled by Skipper Seabold from FRED and the US Bureau of Labor Statistics, with source access dated 15 December 2009. The statsmodels dataset documentation identifies it as public domain:
https://www.statsmodels.org/stable/datasets/generated/macrodata.html

The analysis uses real GDP and real personal consumption expenditure (billions of chained 2005 dollars, seasonally adjusted annual rates). Real investment is inspected in training stationarity tests and excluded from the I(1) system because its trend-stationarity diagnostics differ. All original columns are preserved for traceability.

Important: these are historical revised values, not a sequence of real-time release vintages. Chronological slicing prevents future rows entering a fit, but cannot remove revision hindsight or publication lags already embedded in the dataset. Results are pseudo-out-of-sample. They do not substantiate present-day UK forecasts or a lending model.

Extraction: `statsmodels.api.datasets.macrodata.load_pandas().data.to_csv('us_macro.csv', index=False, float_format='%.10g')`.
`manifest.json` records exact input bytes.
