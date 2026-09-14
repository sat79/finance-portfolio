# Trading strategy research
This branch contains executable research for BTC/USDT and ETH/USDT spot.
It is not a live trading bot. [Executed results](reports/RESULTS-2026-09-14.md): 17 tests passed; the historical strategy family did not meet the requested targets. See RESEARCH-SPEC.md and reports/KROWN-META-SIGNALS-REVIEW.md for the original hypotheses.

## Run
Use Python 3.12:
```sh
python -m pip install -r trading-bot-v2/requirements.txt
python -m unittest discover -s trading-bot-v2/tests -v
python trading-bot-v2/src/research.py
```

The research workflow runs the same commands on GitHub. Results are attached to its run as an artifact, including trade ledgers, daily equity, training selections, all candidate results and data checksums.

## Fixed experiment
Thirteen variants: six intraday SMA21 pullback/reclaim variants; two four-hour pullbacks; one daily SMA200 rebound with half at 3R and a trailing remainder; four confirmed hidden-divergence variants.
BTC is primary. ETH is a fixed robustness check.
Price archives cover January 2018 through August 2026; reported screening begins January 2020.
Rolling evaluation uses the preceding 24 months to choose 2R versus 3R within each family and asset by net return, skipping families without a positive training result. The selected modules share cash and risk limits over the following six months. The final fold may be shorter. All training candidates are retained.
Both normal and doubled assumed fees/slippage are evaluated. Exit selections use normal-cost development results and remain unchanged in the cost stress run.

## Execution assumptions and implementation clarifications
Five-minute execution throughout; higher-timeframe candles are complete and strictly earlier than the signal close. Stops are checked on entry bars and before targets where both are touched. Gap stops use the next observed open. Take-profit fills receive no favorable gap improvement. All exits conservatively receive slippage, including limit targets.
C's trailing remainder activates after its partial target; it uses the maximum completed daily high observed since entry, less three current daily ATR, and ratchets only at the next execution open.
Missing candles are never filled with tradable prices. Incomplete aggregated candles invalidate indicators. An open trade crossing missing data is flagged and cannot establish a passing result.
BTC quantity step 0.00001, ETH step 0.0001 and minimum order notional 10 USDT are fixed research assumptions, not reconstructed historical exchange filters.
Simultaneous modules use the original timeframe priority, then strategy name, then symbol. Maximum one open position per asset, 0.5% initial risk per position, 25% initial position cap, 1% combined planned risk and 50% combined allocation.
Daily boundary liquidation may create an additional fill compared with uninterrupted holding.

## Limits
Results are retrospective and have not yet been prospectively validated. Wilson hit-rate intervals do not correct for serial dependence. Block-bootstrap uncertainty and historical lot-rule reconstruction remain to be implemented. Drawdown measured at five-minute closes can understate intrabar drawdown. Gap-affected results remain provisional.
No Meta Signals archive is included and these strategies do not reproduce its proprietary algorithm.
The execution status must be checked in the latest workflow; code existing in this branch does not mean the data run completed successfully.

## Data source
[Binance official archives and checksums](https://github.com/binance/binance-public-data).
