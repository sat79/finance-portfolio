# BTCUSDT strategy research

Current authorized research scope: **BTCUSDT long and short perpetual futures, maximum 5x leverage**, with stop-based position sizing and 0.5% planned risk per trade. See the [futures research amendment](FUTURES-RESEARCH-AMENDMENT.md). This futures version has not yet been backtested.

The completed studies below evaluated BTCUSDT spot, long only, with protective stops, take profits and cost-aware historical evaluation. Research only; no live orders.

## Latest executed round
[Round 3 results](reports/BTC-ROUND-3-RESULTS.md) compare twelve configurations using daily regimes, confirmed Fibonacci retracements, RSI, hidden divergence, range entries and fixed/adaptive exits across 1h and 4h timeframes.

The highest-return new full-period screen returned +4.69% from January 2020 through August 2026, with 47.0% wins over 66 positions, 1.47 payoff and 1.30 profit factor. It was selected with hindsight, and one position crossed a data gap. The rolling selection lost 0.71% at normal costs and 1.68% at doubled costs over 23 positions. **The 60% hit-rate target is not established; this strategy is not approved for live deployment.**

Thirty-eight implementation tests passed. An independent GitHub run reproduced all 42 summary rows. Daily regime data now come from separately verified daily archives; execution gaps remain flagged. The report separates this correction from strategy changes and retains the superseded preliminary results.

## Research record
- [Round 3 specification and data-method amendment](BTC-ROUND-3-SPEC.md).
- [Round 3 full results, ledgers and manifests](reports/btc-round-3-full-results.zip).
- [Round 3 comparison CSV](reports/btc-round-3-comparison.csv).
- [Round 3 machine-readable snapshot](reports/btc-round-3-results.json).
- [Round 2 results](reports/BTC-ROUND-2-RESULTS.md).
- [Original research results](reports/RESULTS-2026-09-14.md).
- [Krown and Meta Signals public-source review](reports/KROWN-META-SIGNALS-REVIEW.md).

## Reproduce
[Open the pinned round 3 notebook in Colab](https://colab.research.google.com/github/sat79/finance-portfolio/blob/research/trading-bot-v2/trading-bot-v2/notebooks/BTCUSDT-Round-3.ipynb), or use Python 3.12:

```sh
python -m pip install -r trading-bot-v2/requirements.txt
python -m unittest discover -s trading-bot-v2/tests -v
python trading-bot-v2/src/btc_round3.py
```

The notebook pins source commit ade55f92b8d4adb35a06187603390ad5e2f62810. [Independent workflow run](https://github.com/sat79/finance-portfolio/actions/runs/34910758348). Full workflow artifacts have 30-day retention; this repository also stores a permanent result archive.

## Assumptions
Official Binance five-minute and daily archives from 2018 onward; evaluation begins in 2020. Normal costs are 0.10% fees and 0.02% slippage each side; zero and doubled costs are replayed. Initial account 10,000 USDT, 0.5% planned trade risk, 25% initial position allocation, no leverage. Downtrend policy is cash, not short selling.

Next-open entries, confirmed pivots, conservative stop-first intrabar handling, cost-aware stops and quantity sizing are implemented. All historical periods are research-exposed; multiple testing, sparse samples, fixed lot-size assumptions and unobserved execution gaps limit conclusions. The tests verify implementation, not future profitability.

No exchange credentials, proprietary signal archive, live execution or recurring monitoring are included.
