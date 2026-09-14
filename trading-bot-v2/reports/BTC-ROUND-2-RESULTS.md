# BTCUSDT research round 2, results
Recorded 14 September 2026. Status: executed retrospective research; requested performance not established.

## Outcome
None of the twelve new configurations establishes the requested 60% net win rate with average net wins at least 1.5 times average net losses. The rolling combined account fails the objective and loses under both cost assumptions.

The strongest normal-cost full-period screen is E-4h-3R, the four-hour compression breakout with a full 3R target. Its 51 positions produced a 41.2% net hit rate, 1.54 profit factor, +6.46% total return and about 4.23% maximum five-minute-close drawdown. Doubled-cost total return is +3.38%. This is an exploratory candidate selected by looking at the complete screen, not a validated winning strategy.

Its Wilson hit-rate interval is 28.8 to 54.8%. Its three-month block-bootstrap interval for mean net R per position is -0.317 to 0.850, spanning zero. Sparse trades and prior exposure to the history limit the evidence.

## Completed work
- BTCUSDT spot only; long only; no leverage, live orders or signal-provider replication.
- Three new hypotheses: compression breakout (E), support sweep/reclaim (F), oversold rebound (G).
- Twelve fixed configurations with full 2R or 3R targets and protective structural/ATR stops.
- 36 full-period screen rows: twelve rules x zero, normal and doubled costs.
- 14 rolling evaluation folds, each using only the preceding 24 months for selection.
- 26 implementation tests passed, including future-data perturbation, stop/target ordering, entry-bar protection, explicit holding limits and data handling.
- Source commit: fb3cda9dd74adde5d960287ec8e1d48e75bde351.
- [Successful execution](https://github.com/sat79/finance-portfolio/actions/runs/34887205329).
- [Complete downloadable results](https://github.com/sat79/finance-portfolio/actions/runs/34887205329/artifacts/10365097736), including ledgers, daily equity, yearly/monthly returns, training trials, settings and archive checksums. GitHub artifact retention is 30 days; the summary screen and fold rows are also permanently recorded alongside this report.
- [Reproduce in Colab](https://colab.research.google.com/github/sat79/finance-portfolio/blob/research/trading-bot-v2/trading-bot-v2/notebooks/BTCUSDT-Round-2.ipynb).

## Period and assumptions
Official Binance five-minute archives cover January 2018 through August 2026. Evaluation covers January 2020 through August 2026; the first two years are development/warmup history. No new prospective observations are represented.

Each independent screen begins with 10,000 USDT, risks a planned 0.5% per position and caps initial BTC allocation at 25%. Normal costs assume 0.10% fee plus 0.02% spread/slippage each side. Stress doubles both. Prices, fills, size and the cost-distance entry filter are replayed in each scenario: differences in return are not a pure fee subtraction because trade selection and outcomes can change. The zero-cost scenario is diagnostic and cannot choose the rolling strategy.

The loader records 241 shifted candles and 1,847 unavailable/blocked grid intervals over the complete 2018-2026 archive. Shifted candles are not rounded; overlapping grid intervals are blocked. Any screen trade crossing unavailable price history is flagged as provisional. All rolling combined trades were free of such flags.

## All normal-cost configurations, with cost diagnostics
Returns are total account returns for the full evaluation period, not annual returns. Trades, win rates, payoff and profit factor are from normal costs. E = compression breakout; F = support sweep/reclaim; G = oversold rebound.

| Configuration | Trades | Win % | Payoff | PF | Zero-cost return % | Normal return % | Double-cost return % | Gap trades |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E-1h-2R | 309 | 35.0 | 1.53 | 0.82 | 10.21 | -8.75 | -18.28 | 2 |
| E-1h-3R | 310 | 30.3 | 2.05 | 0.89 | 13.99 | -5.56 | -19.32 | 2 |
| E-4h-2R | 55 | 40.0 | 1.85 | 1.23 | 6.49 | 3.11 | 0.20 | 0 |
| E-4h-3R | 51 | 41.2 | 2.20 | 1.54 | 10.15 | 6.46 | 3.38 | 0 |
| F-15min-2R | 925 | 28.0 | 1.45 | 0.56 | -9.18 | -48.37 | -37.53 | 2 |
| F-15min-3R | 1037 | 23.0 | 1.97 | 0.59 | -8.74 | -50.55 | -60.10 | 4 |
| F-1h-2R | 254 | 30.7 | 1.58 | 0.70 | -2.26 | -15.69 | -24.51 | 1 |
| F-1h-3R | 250 | 28.0 | 1.95 | 0.76 | 0.73 | -13.02 | -24.39 | 1 |
| G-4h-2R | 135 | 37.8 | 1.56 | 0.95 | 3.02 | -2.20 | -6.86 | 0 |
| G-4h-3R | 126 | 35.7 | 1.90 | 1.06 | 7.86 | 2.26 | -4.38 | 1 |
| G-1d-2R | 27 | 40.7 | 1.50 | 1.03 | 0.64 | 0.22 | -0.18 | 0 |
| G-1d-3R | 26 | 42.3 | 1.48 | 1.09 | 0.97 | 0.55 | 0.15 | 0 |

## Rolling combined BTC account
Selection was fixed before this run: within each family, choose the highest-return training configuration only if it has at least 30 completed training trades, positive training return, profit factor above 1 and no gap-affected positions. Otherwise that family is inactive. Resolve overlaps by timeframe priority; only one BTC position can be open. Settings remain fixed for the following six months and the same selections are reused under doubled costs.

| Metric | Normal costs | Doubled costs |
|---|---:|---:|
| Total return | -17.73% | -22.04% |
| Annualised return | -2.89% | -3.67% |
| Completed positions | 137 | 135 |
| Net win rate | 24.1% | 21.5% |
| Average net win / average net loss | 1.56 | 1.47 |
| Profit factor | 0.50 | 0.40 |
| Daily-close maximum drawdown | -17.80% | -22.08% |
| Average exposure | 1.89% | 1.78% |
| Worst month | -3.02% | -3.15% |
| Worst calendar year / partial final year | -7.33% | -8.60% |
| Longest losing streak | 11 | 11 |
| Mean net R | -0.342 | -0.411 |
| Mean net R block-bootstrap 95% interval | -0.497 to -0.165 | -0.545 to -0.248 |

The positive full-period four-hour breakout screen did not make the predeclared rolling selection policy profitable. Selecting that one variant after observing these results would be another retrospective selection, not evidence that the losing combined result can be discarded.

## Interpretation
1. Fifteen-minute support sweeps lose even in the zero-cost diagnostic. Their weakness is not explained solely by fees.
2. One-hour breakouts show positive zero-cost screens that become negative at normal costs. Execution costs matter, but zero-cost results are not tradable returns.
3. Four-hour compression breakouts remain slightly profitable under doubled costs and deserve consideration for a separately specified validation exercise. Current evidence does not establish 60% wins or dependable profitability.
4. The oversold-rebound variants show weak or cost-sensitive results.
5. The rolling combination is rejected. Its normal-cost mean-net-R interval is entirely below zero under the specified bootstrap.
6. Keep the prior failures. Further research should use a new dated hypothesis and prospective observations; do not keep tuning this history to obtain a desired percentage.

## Limits
Five-minute OHLC cannot reconstruct every intrabar sequence, spread or limit fill. Stop-first ambiguity handling is conservative, and drawdown sampling can understate intrabar losses. The historical lot/minimum-notional assumptions are fixed approximations. Gap-affected screen rows remain provisional. The universe is one surviving asset. These periods were already used in research and are not pristine holdouts.

Wilson intervals assume independent trials. Circular three-month block resampling only approximates temporal dependence; sparse samples and nonstationary markets remain material limitations. Bootstrap intervals do not correct the multiple-testing bias of selecting the best full-period row. No live/paper monitoring process was started.

## Files
- BTC-ROUND-2-SPEC.md contains the rules recorded before execution.
- btc-round-2-results.json preserves all 36 compact screen rows and 28 cost-specific fold rows.
- btc-round-2-comparison.csv provides the screen in spreadsheet-ready form.
- Full artifact: detailed ledgers, daily equity, settings, input checksums, monthly/yearly returns and all training trials.
