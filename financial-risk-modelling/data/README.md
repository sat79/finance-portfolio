# Dataset and provenance
- `sp500.csv`: 5,031 daily adjusted-close observations for the S&P 500, 4 January 1999–31 December 2018.
- Extracted on 12 September 2026 from `arch.data.sp500.load()` in arch 8.0.0; only the adjusted-close column is retained. The arch documentation identifies Yahoo Finance as the upstream source.
- Source documentation: https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_modeling.html
- Reproduction of extraction: `arch.data.sp500.load()[['Adj Close']].rename(columns={'Adj Close':'adjusted_close'}).to_csv('sp500.csv', index_label='date', float_format='%.10g')`.
- Unit: index points. Weekends and exchange holidays are absent by design. No interpolation, forward filling, live download or revised-data refresh is performed by the analysis.
- Index history is not an investable total-return strategy, a UK bank portfolio or borrower-level credit data. No FX, dividends-as-cash, transaction cost or portfolio concentration model is added.
- This is a frozen historical educational dataset. It does not contain COVID-19 or subsequent events.
- Data attribution is separate from the software licence. The upstream market-data redistribution terms have not been independently cleared for a new public repository; resolve this before publishing the included raw CSV, or provide extraction instructions instead. The private review package includes the dataset so the work can be tested now. The proposed website download excludes raw market data and provides `src/prepare_data.py`, which extracts the hash-checked dataset from the installed arch distribution.
- `manifest.json` records the exact supplied CSV hash, not proof of the upstream source's authenticity.
