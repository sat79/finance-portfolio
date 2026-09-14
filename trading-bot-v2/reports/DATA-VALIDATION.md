# Data validation correction
The first historical run stopped before any strategy metrics were calculated.
All 16 accounting/timing tests passed. The checksum-verified BTC archive contained
shifted candle openings, including 2018-02-09 09:58:14.789 UTC, followed at five-minute intervals.
These were incompatible with the assumed UTC grid.

The loader now excludes shifted candles and blocks the standard grid intervals they
overlap. It records every excluded timestamp and every missing/blocked interval in
the generated manifest. It does not round timestamps or manufacture replacement OHLC.
A new regression test checks that shifted candles cannot become tradable regular bars.
Any open trade crossing unavailable data remains explicitly flagged as provisional.

Original diagnostic run:
https://github.com/sat79/finance-portfolio/actions/runs/34879895698
