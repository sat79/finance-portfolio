# Krown and Meta Signals: evidence review and research amendment
Recorded 14 September 2026. Status: public-source review and specified experiments; no new historical backtest has run. This document supplements RESEARCH-SPEC.md without changing its original nine configurations.

## Findings and limits

### Krown
The supplied URL currently presents The Operator Course for Central Command. Its landing page advertises a managed vault and a custom strategy execution platform. It reports 129 closed trades, 43% wins, a 1.55 profit factor and $258.97 lifetime profit after fees, alongside $10,234 assets under management. The advertised 24% annual yield is an objective, not a demonstrated annual return. These are vendor claims, not independently reconciled results. The page also discloses exchange referral compensation.

The public landing page supplies no complete trade ledger, dated equity curve or executable entry/exit rules. Course enrollment leads to checkout; no enrollment or deposit was completed. The review covers the accessible landing page, not the enrolled curriculum.

Source: [Krown course](https://krown-trading.teachable.com/p/cpro).

Assessment: it does not establish the requested 60% hit rate. Automation capability is not evidence of a profitable entry signal. Its reported profit factor means aggregate winning profit is 1.55 times aggregate losing profit; it does not mean the average winner is 1.55 times the average loser.

### Meta Signals identity and disclosed methodology
This review concerns metasignals.io, which lists Eric Krown among its founders. If a different service was intended, these conclusions do not transfer.
Source: [Meta Signals](https://metasignals.io/).

The provider describes The Jewel as proprietary, combining momentum, volatility, a Fibonacci component and multiple time periods, and says its alerts incorporate Jewel data. Exact formulas, thresholds and versioned historical signals were not obtained. A reconstruction would be an independently defined hypothesis, not a verified replica.
Source: [The Jewel](https://metasignals.io/jewel).

A separate RSI-divergence product discloses Wilder RSI on closing prices, length 14, an RSI EMA length of 12, a 28-bar lookback and candle-close confirmation beyond a wick. It timestamps confirmation rather than the earlier turning point. These settings do not fully specify its pivot selection or the main Pro algorithm.
Source: [RSI divergence](https://metasignals.io/rsi-div).

Lite adds human selection to algorithmic alerts. Its historical discretionary selections cannot be regenerated from prices alone.
Source: [Lite FAQ](https://metasignals.io/lite/faqs).

The trading guide describes immediate entry, target-specific outcomes and stop invalidation at candle close. It discusses TP1 around 0.75R and larger later targets, and acknowledges that TP3 may fail more often than succeed. A close-based exit can exceed the nominal stop distance. A trader who changes entry, exit or allocation rules changes the measured strategy.
Source: [Trading guide](https://metasignals.io/traders).

### What is their hit rate?
Not independently verified. The dashboard, historical-performance and pending/resolved pages returned navigation without readable statistics or an export in this session. This access limitation is not evidence that the underlying data do not exist.

Sources: [Dashboard](https://metasignals.io/dashboard), [Historical performance](https://metasignals.io/dashboard/historical-performance), [Pending/resolved alerts](https://metasignals.io/dashboard/pending-resolved-alerts).

Do not substitute selected winning screenshots, testimonials or another similarly named service's results. Do not interpret a percentage beside TP until its field definition is known: it could represent price distance, leveraged return, historical target frequency or a predicted probability.

## How to audit the signal percentages

Request one original alert with its field legend, followed by a complete date-bounded export that includes original publication times, versions, edits, cancellations, unresolved calls and losses. Preserve source records and stable signal IDs. The companion CSV is an empty collection template, not performance evidence.

Separate:
- Target-touch frequency for TP1, TP2 and TP3, each with an explicit denominator and observation horizon.
- Net profitable completed positions, aggregating every partial exit, fee and funding payment.
- Average net win/loss ratio, profit factor, expectancy and account drawdown under a fixed allocation policy.
- Forecast calibration: if a field means 70% predicted probability, assess whether about 70% of eligible subsequent cases resolve as specified, with sample counts and uncertainty.

For probabilities published per target, evaluate each horizon separately using reliability bins and Brier scores on subsequently observed outcomes. Cluster uncertainty by overlapping time periods and assets. An unresolved signal is neither an automatic loss nor an automatic win; report unresolved counts and use a predefined maturity horizon. Never remove difficult unresolved calls to improve results.

Replay original signals at the first executable price after receipt, allowing latency. Distinguish unfilled limit entries from losses and prohibit fills before publication. Use the original exchange and instrument; spot candles are not a faithful substitute for perpetual futures, which require funding and instrument-specific prices.

Freeze separate exit policies: full TP1, full TP2, full TP3, and equal thirds at all three targets when available. Specify remaining-position stops and expiry in advance. Replay the provider's documented close-based stop separately from a protective touch-stop version. Report stop overshoot and ambiguous intrabar ordering; never credit target first when the price sequence is unknown.

A signal reaching TP1 can still lose overall. Hypothetically, selling one third at +0.75R and losing 1R on each remaining third gives -0.4167R before costs. With full exits at +0.75R/-1R, 60% winners yield only +0.05R per trade before costs. These are arithmetic illustrations, not provider results; close-based stop overshoot can make the latter loss assumption too optimistic.

## Research amendment D: confirmed divergence within an uptrend

Purpose: test whether a momentum pullback inside an established trend improves entry quality relative to the existing moving-average ideas. This is an original, fully specified experiment inspired by disclosed concepts. It does not reproduce The Jewel, its Fibonacci component, Pro or Lite.

Inherit the original specification's data validation, capital limits, fees, next-bar execution, stop-first ambiguity handling and walk-forward rules unless explicitly replaced below. BTC/USDT spot is primary; ETH/USDT spot is a predeclared robustness check. Long only.

Run four configurations: entry timeframe 4 hours or 1 day, crossed with full-position profit targets 2R or 3R. This increases the total research family from nine to thirteen new configurations. Report every configuration; selecting among more trials increases selection bias.

Definitions:
1. Compute Wilder RSI(14) from completed closing prices. Seed smoothed gains and losses with their first 14-change arithmetic means; update with weight 1/14. If both are zero, RSI=50; if loss alone is zero, RSI=100. Use unsmoothed RSI for this experiment; do not claim equivalence to the provider's RSI EMA.
2. A price pivot low at bar p requires low[p] strictly below lows at p-2, p-1, p+1 and p+2. Ties do not qualify. The pivot is first known at the close of p+2.
3. Use consecutive confirmed pivot lows p1 and p2 separated by 3 to 28 bars. Hidden bullish divergence requires low[p2] > low[p1] and RSI[p2] < RSI[p1].
4. Starting at close p2+2, look for the first candle close strictly above high[p2], no later than close p2+6. The first such close is the only candidate for that pivot pair; if it fails the trend gate, skip the pair.
5. The trend gate at the candidate close requires close > SMA21 > SMA200 and SMA200 greater than its value 20 bars earlier, all on the entry timeframe. The 4-hour variant additionally requires the last strictly earlier completed daily close above its daily SMA200. The daily variant has no extra higher-timeframe gate.
6. Require no intervening low below low[p2] through the signal close. Consume each pair once, including signals skipped due to an existing position or capital limits.
7. Enter at the next execution bar open. Freeze the signal's ATR(14), defined as in the original specification, and low[p2]. The hard stop is the lower of entry minus 2 ATR and low[p2] minus 0.25 ATR. Reject entry at or below the structural stop. R is entry minus the final stop.
8. Exit the entire position at the configured 2R or 3R target, the protective touch stop, or the next execution open after an entry-timeframe close below SMA200. Also exit after 30 elapsed days for the 4-hour version or 365 elapsed days for the daily version. Stops and targets remain active until that scheduled exit.
9. Do not move the stop to break-even, scale out or add a volume/Fibonacci threshold in these four configurations. Any such extension requires another recorded experiment. Retain the original estimated-cost target-distance gate.

Backtest sequencing:
- Run the original intraday pullback variants and this longer-timeframe divergence candidate separately before any shared-capital combination.
- Use the longest verified history available, with 24-month development and 6-month evaluation windows advanced six months. Choose any exit variant using development data only.
- Previously examined history is retrospective evaluation, not untouched proof. Reserve genuinely later observations for prospective validation.
- Validate future-data perturbation, pivot confirmation delay, fees, entry timing, gaps and close/touch-stop distinctions before interpreting returns.
- Report net win rate with uncertainty, trade count, payoff ratio, profit factor, expectancy, returns, drawdown, turnover and doubled-cost results against relevant benchmarks.
- The research target remains at least 60% net winners with average net wins at least 1.5 times losses; jointly this implies profit factor at least 2.25 on the same sample. No public information reviewed demonstrates that this candidate achieves it.

## Current completion state
Completed: source review, performance-definition audit, recorded strategy rules and empty signal collection template.
Not completed: independent provider signal replay, implementation and historical testing of amendment D, or a demonstrated strategy meeting the requested thresholds. The execution workspace is unavailable in this session. No live trading was initiated.
