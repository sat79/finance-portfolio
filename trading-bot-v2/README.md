# BTCUSDT strategy research

Current focus: BTCUSDT spot, long only. The project compares explicit trading rules with protective stops, fixed profit targets and realistic cost assumptions. It is research, not a live trading service.

## Latest executed round
[BTCUSDT round 2 results](reports/BTC-ROUND-2-RESULTS.md) cover twelve new configurations, with 26 passing implementation tests. The strongest full-period screen was a four-hour compression breakout with a 3R target: 41.2% wins over 51 positions and +6.46% total account return for January 2020 through August 2026. Doubled-cost return was +3.38%.

That result does not establish the requested 60% hit rate. The predeclared rolling combined account lost 17.73% at normal costs and 22.04% at doubled costs. It is rejected for deployment. Read the report for uncertainty, trade counts, full comparisons and limitations.

## Research record
- [Round 2 rules recorded before execution](BTC-ROUND-2-SPEC.md).
- [Latest spreadsheet-ready comparison](reports/btc-round-2-comparison.csv).
- [Latest screen and rolling results](reports/btc-round-2-results.json).
- [Original thirteen-configuration results, including earlier ETH comparison](reports/RESULTS-2026-09-14.md).
- [Original research contract](RESEARCH-SPEC.md).
- [Krown and Meta Signals public-source review](reports/KROWN-META-SIGNALS-REVIEW.md).

The prior studies remain available; the current workflow evaluates BTC only.

## Reproduce
[Open the BTCUSDT notebook in Colab](https://colab.research.google.com/github/sat79/finance-portfolio/blob/research/trading-bot-v2/trading-bot-v2/notebooks/BTCUSDT-Round-2.ipynb), or use Python 3.12:

```sh
python -m pip install -r trading-bot-v2/requirements.txt
python -m unittest discover -s trading-bot-v2/tests -v
python trading-bot-v2/src/btc_round2.py
```

The GitHub workflow runs the same checks and attaches data manifests, ledgers, daily equity, all training candidates and summary results. Full run artifacts have 30-day retention; compact result snapshots are permanently saved here.

The original study remains reproducible through notebooks/Run-Research.ipynb, pinned to its original tested source.

## Assumptions
Official Binance five-minute archives from 2018 onward; evaluation begins in 2020. Normal costs are assumed to be 0.10% fees and 0.02% spread/slippage each side. The study also includes zero and doubled costs, next-open entries, conservative stop-first handling, gap flags and cost-aware position sizing.

Rolling selection uses preceding data only, but all historical periods have already influenced research. The tests establish implementation checks, not profitable future performance. Quantity steps and minimum notional remain fixed research assumptions. Sparse samples, missing data, approximate fills and multiple-testing bias limit conclusions.

No exchange credentials, proprietary signal archive, live execution or recurring monitoring are included.
