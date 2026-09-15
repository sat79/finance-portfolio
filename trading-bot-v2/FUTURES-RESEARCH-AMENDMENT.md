# BTCUSDT futures research amendment
Recorded 15 September 2026 following the instruction permitting long and short positions with maximum leverage of 5x.

## Authorized research scope
- Pair: BTCUSDT.
- Directions: long and short.
- Research instrument: USDT-margined perpetual futures. Binance public data are the research data source, not a selection of the user's live trading venue.
- Maximum permitted contract leverage setting: 5x.
- Maximum gross entry notional: 5 times current account equity, across all open positions.
- Size from the protective stop and retain the existing 0.5% planned equity risk per position. Use the smaller of risk-based size and the leverage/notional limit. Leverage is a ceiling, not a target.
- Include estimated entry/exit fees and adverse slippage in stop-risk sizing. Funding and price gaps can cause realized losses to exceed planned stop risk.
- One directional position at a time; no simultaneous hedged long/short positions, martingale, or loss-driven size increases.
- Every entry requires a valid protective stop and an explicit take-profit/exit policy.
- Long, short and combined results must be reported separately across uptrend, downtrend, sideways and transition conditions.
- Compare 1x, 2x, 3x and 5x leverage ceilings with the same risk budget and trading rules. Do not mechanically multiply prior spot returns by leverage.
- This updates research permission only. No live orders or exchange-account settings are authorized or changed.

## Required futures execution work
Use native futures execution candles, independently validated higher-timeframe futures candles, historical funding events and mark-price observations. Charge or credit funding according to position direction and event-time exposure. Funding timestamps can include milliseconds after a nominal boundary: preserve them and explicitly model event ordering instead of silently rounding.
Model signed long/short P&L, margin requirements, mark-price liquidation risk and the leverage ceiling. Document maintenance-margin tiers and liquidation assumptions; do not claim exchange-exact liquidation using unverified historical parameters. Enforce the ceiling at entries and additional exposure, and explicitly define deleveraging when adverse price movement raises account exposure.
Keep gaps flagged. Do not infer short futures performance from inverted spot-account results.

## Status and data-source check
The new scope is recorded; a long/short futures backtest has not yet been executed. The latest completed study remains the round-3 spot study. Its results are not futures results.
A read-only source check on 15 September 2026 successfully retrieved August 2026 BTCUSDT 5-minute perpetual trade candles, 5-minute mark-price candles and funding-history archives and inspected their CSV headers. This establishes sample availability only; it is not complete-history validation or checksum verification.

Sources:
- [Binance public-data documentation](https://github.com/binance/binance-public-data)
- [USD-M futures market-data documentation](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data)
- [Futures trade-candle sample](https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2026-08.zip)
- [Futures mark-price sample](https://data.binance.vision/data/futures/um/monthly/markPriceKlines/BTCUSDT/5m/BTCUSDT-5m-2026-08.zip)
- [Funding-history sample](https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2026-08.zip)
