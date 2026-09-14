# Unilever equity valuation and model review

Retrospective FY2024 finance study covering 2020–2024 performance, DuPont ROE, FCFF DCF, residual income and trading multiples. Reviewed for Satvik Sahni's portfolio.

## Evidence

- [Reviewed Excel model](models/Unilever-Valuation-Reviewed.xlsx)
- [Analytical review](reports/Review.md)
- [Calculation checks and limitations](reports/Validation.md)
- [Independent Python arithmetic check](src/verify_model.py)

## Reproduce the arithmetic

Extract the archive and open a terminal in `unilever-equity-valuation`. Requires Python 3.10+ and no third-party packages. Tested on Linux with Python 3.12.14.

```bash
python3 src/verify_package.py
python3 -m unittest discover -s tests -v
python3 src/verify_model.py
```

The verifier independently reproduces 98 saved formula results, including the FCFF build, enterprise-to-equity bridge, full sensitivity grid and residual-income build. It checks saved Excel values; it does not run Excel formulas or validate external source evidence.

The default DCF value is €63.87/share and the residual-income value is €54.94/share. These are retrospective scenario outputs, not current targets. In Excel, `DCF!B53` selects manual WACC (0) or illustrative calculated WACC (1). Invalid weights and discount/growth combinations are rejected.

## What this review does and does not establish

Sensitivity headers now control the calculations. Historical input duplication and summary weighting were reduced. The weighted result is labelled a scenario, reflecting illustrative weights. Full-year 2024 results were published after year-end, so this is not a hindsight-free backtest.

Peer dates/definitions, minority-interest treatment, valuation-date diluted shares and clean-surplus consistency still need substantiation. Terminal residual income does not explicitly fade ROE. The old report's rating and fade description should not be used with this reviewed copy. The accessible generated files are not proof of the exact original MSc submission.

Source references are retained in the workbook. No open-source licence has been assigned. Checksums detect accidental changes; they do not prove authenticity.
