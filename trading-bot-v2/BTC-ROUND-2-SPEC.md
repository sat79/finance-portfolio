# BTCUSDT research, round 2
Recorded 14 September 2026 before the new historical run. All preceding experiments remain in the research record.

## Scope and objective
BTCUSDT spot, long only, no leverage. ETH is excluded from this round.
Target: at least 60% net profitable completed positions, average net wins at least 1.5 times losses, positive doubled-cost expectancy and controlled drawdown. These are research targets, not promised results.
This is a new economic-hypothesis comparison, not a proprietary signal-service replication.

## Fixed twelve-configuration matrix
Each of the following six entry rules has full-position targets at 2R and 3R. Stops are hard protective stops; no scaling out or discretionary overrides.
All values are from completed candles. Signal orders execute at the next five-minute open.

E: compression breakout, 1-hour and 4-hour entries.
- Range width = (highest high over 20 bars minus lowest low over 20 bars) / SMA21.
- A compressed bar has range width below the 20th percentile of the preceding 120 range widths, excluding that bar.
- At least one of the preceding 12 bars was compressed.
- Close exceeds the highest high of the preceding 20 bars, and the previous close did not exceed its own preceding-20-bar high.
- Higher-timeframe gate: the strictly earlier completed 4-hour close (for 1h entry) or daily close (for 4h entry) exceeds its SMA200.
- Initial stop is the lower of entry minus 1.5 ATR (1h) or 2 ATR (4h), and the broken preceding-20-bar high minus 0.25 ATR.
- Exit on higher-timeframe gate loss, entry-timeframe close below SMA21, protective stop, target or a 2-day (1h) / 30-day (4h) holding limit.

F: support sweep and reclaim, 15-minute and 1-hour entries.
- Low trades below the lowest low of the preceding 20 bars; close returns above that prior support.
- Candle is bullish, and close is in the top 35% of its high-low range.
- Wilder RSI14 is below 45 at the close.
- The strictly earlier completed 4-hour close exceeds its SMA200.
- Stop is the lower of entry minus 1.5 ATR and signal low minus 0.25 ATR.
- Exit on gate loss, protective stop, target or a 2-day holding limit.

G: oversold rebound, 4-hour and daily entries.
- Wilder RSI2 crosses above 10 from at or below 10 on the immediately previous bar.
- Close exceeds the preceding close.
- For 4h, the strictly earlier completed daily close exceeds daily SMA200. For daily, close exceeds SMA200 and SMA200 exceeds its value 20 days earlier.
- Stop is the lower of entry minus 2 ATR and the minimum of the last three lows minus 0.25 ATR.
- Exit on gate loss, protective stop, target or a 10-day (4h) / 20-day (daily) holding limit.

## Data and execution
Reuse the corrected, checksum-verified five-minute archive loader, January 2018 through August 2026. Screen January 2020 through August 2026. Shifted candles are excluded and overlapping grid intervals blocked; missing prices are not filled.
ATR is the simple mean of 14 true ranges. RSI uses Wilder smoothing, seeded from the first period's changes and restarted after a gap. Existing next-open, stop-first ambiguity, gap-stop and cost-aware sizing rules remain.
Initial capital 10,000 USDT; planned risk 0.5%; maximum initial BTC allocation 25%; at most one open BTC position.
Research quantity step 0.00001 BTC and minimum notional 10 USDT remain fixed assumptions, not reconstructed exchange history.
Reject a target whose gross gain is less than three times estimated round-trip costs. Report zero, normal and doubled cost scenarios. Normal: 0.10% fee + 0.02% slippage/spread each side.
Five-minute OHLC replay is an approximation, not tick/order-book execution.

## Rolling combination, fixed before observing results
For each 6-month evaluation fold, evaluate every new configuration on only the preceding 24 months at normal costs.
Within each family E/F/G, select the configuration with the highest net account return among those with at least 30 completed positions, positive net return, profit factor above 1 and zero gap-affected positions. Ties resolve by configuration name. Families without an eligible candidate stay inactive.
Selected families share one BTC account in the next fold, with the previously declared timeframe priority (daily, 4h, 1h, 15m), then configuration name. The same selections are reused under doubled costs; screening at zero cost is diagnostic only and cannot select variants.
Close positions at fold boundaries. Keep all candidates, inactive folds and failed tests.

## Evidence and uncertainty
All this history is already research-exposed. Rolling results are retrospective, not pristine out-of-sample proof.
Report Wilson hit-rate intervals and a circular three-calendar-month block bootstrap for mean net R and profit factor, with 2,000 draws and fixed seed 20260914. This approximates temporal dependence and is unstable for sparse trades.
Report all screen rows and rolling combined results, fee totals, exposure, yearly and monthly returns, losing streaks and daily time underwater. Daily metrics can understate intraday drawdown.
No variant is validated merely by passing a point estimate; fewer than 200 evaluation trades is labelled preliminary. No parameter changes will be made in response to this round's results.
