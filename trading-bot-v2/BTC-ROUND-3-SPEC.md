# BTCUSDT research round 3, regime-aware refinement
Recorded before running the new historical comparisons, 14 September 2026.

BTCUSDT spot, long only. Starting capital 10,000 USDT, initial risk 0.5%, maximum initial allocation 25%, no leverage. Downtrend policy is cash; this is not a short-selling test.

## Regime definition, fixed before results
Use completed daily candles: SMA200, its change over 20 days measured in daily simple ATR14 units, and Wilder ADX14.
- Uptrend: close above SMA200, SMA200 change greater than +0.5 ATR, ADX >=20.
- Downtrend: close below SMA200, SMA200 change below -0.5 ATR, ADX >=20.
- Sideways: ADX <20 with all required indicators available.
- Transition: other fully observed conditions.
- Unknown: unavailable indicators.
Trade only uptrend or sideways signals. Exit on a change away from the entry regime. Report downtrend, sideways, uptrend, transition and unknown periods separately. These are causal rule-based labels, not discretionary classifications made after seeing returns.
Signal-time regime uses a daily candle closing strictly before the entry candle closes.

## Uptrend entry: Fibonacci retracement with confirmation
A pivot high/low must be strictly above/below its two neighbours on each side; it becomes available only two bars later.
An active impulse runs from the latest confirmed low before a subsequently confirmed high. Freeze these anchors when the high is confirmed. Require an impulse at least 3 ATR at that high. Do not use future pivots.
For no more than 20 bars after the impulse high, seek a retracement into the 38.2%-61.8% zone within the last three completed bars. No low since the impulse high may breach the anchor low.
Signal close must exceed the 50% retracement level and previous bar high, remain below the impulse high, and have rising RSI14 above 40.
Two predeclared confirmations:
1. RSI only.
2. RSI plus hidden bullish divergence: the latest two confirmed price lows, 3-28 bars apart, have a higher second price low but lower RSI14. The second low is after the impulse high and no more than eight bars old.
Only the first qualifying signal per impulse is emitted, including signals later skipped due to an open position.
Stop is the lower of entry minus 1.5 ATR and the last five lows minus 0.25 ATR.

## Sideways entry: lower-band rejection
SMA20 and population standard deviation over 20 bars define a lower band at SMA20 minus 2 standard deviations.
The signal candle trades below that band and closes back above it, closes above its open, and has rising RSI14 below 40.
Use the same structural/1.5-ATR initial stop. No Fibonacci or divergence gate is added to this range module.

## Twelve combined rule configurations
Entry timeframe: 1 hour or 4 hours.
Uptrend confirmation: RSI or RSI plus hidden divergence.
Exit policy:
- Fixed full 1.5R target.
- Fixed full 2R target.
- Adaptive: full 3R target, with cost-adjusted breakeven after a completed entry-timeframe bar reaches 1R; after a completed bar reaches 2R, also trail the highest completed high since entry by 2 ATR. Ratchet stops only at the next execution open, never from future/current unfinished candles. In sideways entries, additionally exit at next open when a completed close reaches its SMA20.
Fixed policies do not have the sideways mean exit or breakeven.
All policies also exit on regime change, stop, target or a 5-day (1h) / 20-day (4h) limit. Every partially or fully closed position remains one position for win-rate purposes; there are no partial exits in round 3.

## Evaluation
Same verified five-minute BTC archive, January 2018 through August 2026; January 2020 through August 2026 retrospective screen. No prices are imputed through missing/shifted candles.
Zero, normal and doubled costs are separate replays. Normal costs remain 0.10% fee and 0.02% slippage each way. Cost-distance entry filter remains 3x estimated round-trip cost.
The frozen E-4h-3R round-2 breakout is rerun as a baseline, without changing its rules.
Rolling combination: preceding 24 months select one of the twelve configurations by highest normal-cost net return, requiring at least 20 training positions, positive mean net R, positive return and zero gap-affected positions. Ties use configuration name. If none qualify, hold cash for the next six months. Fix that configuration through the fold; use identical selection in the doubled-cost replay. Forced fold liquidation stays unchanged.
This round adds twelve trials to the prior research family. Selection and all failures must be disclosed.

## Regime reporting and uncertainty
Show closed-position metrics by entry regime, plus daily account returns grouped by the regime known at that day's opening. Include number of days, compounded daily account returns, BTC open-to-close returns for the same days and downside days. Regime subsets are non-contiguous slices, not independent investable portfolios.
Wilson hit-rate intervals and a fixed-seed circular three-month, 2,000-draw bootstrap for mean net R and profit factor are retained.
Report whole-account results, trade counts, payoff, costs, worst month/year, drawdown and exposure, rather than judging isolated win rates.
All historical periods are research-exposed; neither chronological selection nor bootstrap removes selection bias. The 60%/1.5 payoff target remains unproven until supported by sufficiently broad evaluation and later forward observations.

