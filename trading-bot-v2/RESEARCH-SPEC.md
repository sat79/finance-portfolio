# Trading bot v2 — research specification
Recorded 14 September 2026. Status: specified, not historically backtested or approved for live trading.

## Objective
Develop a cost-aware, long-only research bot with separate intraday, swing and position-trading modules. Begin with BTC/USDT spot, matching the prior research. ETH/USDT is a predeclared secondary robustness instrument, not a substitute chosen after seeing BTC results. No leverage or broker credentials are required for the research phase.

The requested goal is at least 60% profitable completed trades with materially larger average wins than losses. This is a target to test, not a promised result. Define wins by total position P&L after all costs; partial exits do not count as separate wins.

Illustrative joint acceptance targets:
- Net win rate >= 60%.
- Average net winning trade / absolute average net losing trade >= 1.5.
- These imply net profit factor >= 2.25 when the same closed-trade sample is used.
- Positive net expectancy, satisfactory exposure-adjusted returns, and a proposed maximum account drawdown of 10% under the specified sizing.
- Report uncertainty and trade counts. Fewer than 200 evaluation trades per intraday configuration is preliminary, not evidence of a dependable 60% rate. Longer-term variants may require years of forward observation.
- Positive expectancy under doubled assumed trading costs.
No candidate is to be declared successful merely because its best historical parameter combination meets a threshold.

## What the previous research established
The completed 13 September study tested a fresh SMA21 cross above SMA200 on Binance BTC/USDT, with completed 4-hour and daily uptrend filters. The January 2025–August 2026 evaluation reported:

| Entry | Total account return | Trades | Net win rate | Profit factor |
|---|---:|---:|---:|---:|
| 5 minutes | -9.25% | 139 | 19.4% | 0.33 |
| 15 minutes | -2.49% | 44 | 27.3% | 0.56 |
| 1 hour | -1.72% | 11 | 18.2% | 0.14 |

These are prior saved results, not new calculations. Each used a separate 10,000 USDT simulation, 0.5% planned risk per trade, a 25% position cap and baseline costs of 0.12% each way. The prior Bitcoin Fear & Greed overlay did not make the variants profitable.

The earlier daily equity tests also underperformed a fully invested benchmark and had low exposure. Long-term near-200-MA and intraday crossover ideas must therefore be evaluated separately rather than merged mechanically.

## Shared definitions
All moving averages are simple moving averages, preserving the previous MA convention. ATR is the simple mean of the last 14 completed true ranges. Do not silently substitute EMA or Wilder ATR.
- Timestamp candles by opening time, retain their actual close times, use UTC, and verify exchange timestamp units.
- Higher-timeframe inputs must be closed strictly before the entry signal closes.
- Signals use completed candles. Fill at the next available execution-bar open, never at the signal close.
- At signal time, freeze ATR and the structural low used to define the initial stop.
- Do not add RSI, MACD, multiple sentiment thresholds or discretionary chart patterns to the first matrix.

## Candidate A: intraday trend pullback and reclaim
Test 5-minute, 15-minute and 1-hour entry candles separately. Use a common five-minute execution grid.

Higher-timeframe gate:
- The last eligible completed 4-hour close is above its SMA200.
- That 4-hour SMA200 is above its value 20 completed 4-hour candles earlier.
- The previous study's additional daily gate remains a labelled baseline comparison; it is not required by this simpler candidate.

Entry-timeframe conditions at completed candle t:
1. SMA21[t] > SMA200[t] and SMA21[t-1] > SMA200[t-1].
2. SMA21[t] > SMA21[t-3].
3. At least one of candles t-3 through t-1 has low <= its own SMA21 and close >= its own SMA200.
4. Candle t closes above SMA21[t] and above high[t-1].
5. No open position or unconsumed entry signal exists for this module.
6. The next execution-bar open must still exceed the frozen structural stop; otherwise cancel the entry.

Initial stop: the lower of (entry - 1.5 x signal ATR) and (lowest low from t-9 through t - 0.25 x signal ATR). This deliberately places the stop below both the volatility and structural levels.

Exits, tested as two fixed alternatives:
- A1: full-position take profit at entry + 2R.
- A2: full-position take profit at entry + 3R.
Here R is entry minus initial stop before costs. Stop levels are never widened. No automatic breakeven move is included.
- Ordinary exit when the eligible 4-hour gate fails, or entry-timeframe SMA21 <= SMA200, or holding time reaches 48 hours. Execute at the next bar open.
- Skip a signal when expected full-target cash gain before costs is less than three times estimated round-trip trading costs.
- Re-entry requires a newly completed qualifying signal after the previous position has closed; do not reuse an earlier signal.

## Candidate B: swing pullback
Entry timeframe: 4 hours. Higher-timeframe gate: eligible daily close > daily SMA200 and daily SMA200 > its value 20 daily candles earlier.
Use the same completed pullback/reclaim conditions as Candidate A on 4-hour candles.
Initial stop: lower of entry - 2 ATR and the last ten 4-hour lows minus 0.25 ATR.
Compare full exits at 2R and 3R. Exit on loss of the daily gate, reverse 4-hour MA state, or a 30-calendar-day holding limit.
Use five-minute execution bars for stops and targets where data coverage supports them. Do not compare coarse daily stop handling with fine intraday execution without identifying the difference.

## Candidate C: longer-term 200-day rebound
Entry timeframe: daily. Use daily SMA200 and a 20-day rising-SMA200 check.
- In the last five completed daily candles, at least one low is within 0.5 daily ATR of that candle's SMA200, and none closes more than 1 ATR below its SMA200.
- Signal candle closes above daily SMA200 and above the preceding day's high.
- Enter next eligible execution-bar open.
Initial stop: lower of entry - 2 daily ATR and the lowest of the preceding ten completed daily lows minus 0.25 ATR.
Take profit on half the position at 3R; the remainder uses a 3-ATR trailing stop based only on prior completed daily bars. The trailing stop ratchets upward, applies only from the following execution bar, and never loosens the initial stop.
Exit the remainder if a daily candle closes below SMA200, or after 365 calendar days.
Record each partially exited position as one trade, with fees on each fill. Count its final aggregate net P&L in the win rate.

The fixed first-pass matrix contains nine new configurations: six intraday, two swing and one daily position rule. Keep all nine result rows, including failures. ETH replication does not authorize more parameter search.

## Position sizing and combined account
Maintain the prior 0.5% planned risk per trade and 25% position-notional cap as research defaults. Initial capital: 10,000 USDT for comparability, with results also expressed as percentages and R multiples.
Risk-based size must include estimated entry and stop-exit costs. Cap size by available cash and the position cap; round down to exchange lot size and reject orders below minimum notional.
For amalgamated testing:
- One combined account, no double counting of capital across timeframes.
- Total planned stop risk <= 1% of account equity; total invested notional <= 50%.
- Maximum one open position per asset across all modules.
- Resolve simultaneous signals in this fixed order: daily, 4-hour, 1-hour, 15-minute, 5-minute.
- Test modules independently first. Combining losing modules does not establish diversification or an edge.
These are planned stop-risk limits, not guarantees against gaps, slippage or exchange outages.

## Costs and execution
Baseline assumptions remain 0.10% fee plus 0.02% spread/slippage per side, not a claim about today's account-specific fee tier. Stress doubles both assumptions.
- Charge entry, exit, partial-exit and forced-liquidation costs.
- Stop-first if an execution candle touches both stop and target without finer path evidence.
- A gap below a stop exits at the opening price less slippage, not the stale stop.
- A gap above a limit take-profit receives no improvement beyond the limit in the conservative model.
- Stops apply to the entry execution candle after the next-open fill.
- Trail changes based on a bar's high cannot affect fills earlier in that same bar.
- Reject or explicitly block missing/duplicate candles and malformed OHLC data; never forward-fill tradable prices through an outage.
- Include mark-to-market equity, unrealised losses, end-period liquidation and cash reconciliation.

## Data and validation protocol
Use official exchange OHLCV archives/API with manifests, checksums, retrieval dates and coverage checks. Start with the longest consistent BTC sample available from 2018; shorter-timeframe downloading may be staged. Daily/4-hour and intraday historical coverage must be reported independently.

Existing history through August 2026 has influenced the new hypotheses. It is development evidence, not a pristine holdout:
1. Preserve the old baseline results.
2. Use chronological rolling evaluation, for example 24 months development followed by six months evaluation, rolling six months at a time.
3. Select exits only from the development portion of each fold. Freeze settings through the next evaluation fold.
4. Warm indicators with preceding prices without permitting future price/outcome access.
5. Close positions at fold boundaries or explicitly exclude overlapping trades so training outcomes cannot extend into evaluation.
6. Report all trials and the selection rule. Do not repeatedly test the same holdout until it passes.
7. Call historical rolling results retrospective pseudo-out-of-sample, because these periods are already research-exposed.
8. Only data after the frozen specification can support a prospective trial. No monitoring or recurring paper-trading process has been started.

For uncertainty, report Wilson intervals on hit rates, and time-block bootstrap intervals for expectancy/profit factor. Disclose serial dependence and sparse long-term samples; aggregate counts across correlated assets do not create independent evidence.

## Fear & Greed
Keep sentiment off in the first comparison. If the technical strategy warrants a further experiment, predeclare one overlay: block entries above 75. Use the same rules/costs and the prior 24-hour publication delay, backward-only joins and stale-data blocking. Report its incremental effect separately. Do not sweep sentiment thresholds to manufacture a 60% rate.

## Required output
One comparison table per timeframe plus a combined-account table, including:
- Total return and annualised return where sample duration supports annualisation.
- Net win rate, confidence interval, closed-trade count and no-trade periods.
- Average net win/loss ratio, profit factor and net expectancy.
- Maximum drawdown, worst month/year, longest losing streak and time underwater.
- Average exposure, turnover, costs paid and percentage of candidate signals filtered out.
- Base and doubled-cost results.
- Buy-and-hold and a clearly defined exposure-matched benchmark.
- Separate development, retrospective evaluation and prospective results.
- Full timestamped trade ledger, equity curve, fixed settings and input hashes.

Pass/fail/insufficient-evidence must be explicit. Never present a high hit rate from a handful of trades, winning partial fills, zero fees or future-informed entries as success.

## Implementation checks required before historical runs
Financial accounting, next-bar entry, completed higher-timeframe joins, future-data perturbation, gap stops, same-bar stop/target ambiguity, partial-exit accounting, trailing timing, shared-account limits, duplicate/missing bars, fee stress and fold-boundary isolation.

## Current blocker and next action
The execution workspace failed its initialization handshake in this session; no new historical backtest, data download or live bot has run. This file records the research contract so implementation and evaluation can proceed when execution is available. The draft does not certify a 60% hit rate or any profitability.

## Primary implementation references
- Binance public archive conventions and checksums: https://github.com/binance/binance-public-data
- Binance candle endpoint: https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market
