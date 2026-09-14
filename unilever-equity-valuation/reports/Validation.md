# Calculation and delivery review

Reviewed 12 September 2026. The financial assumptions retain their 11 September 2026 study date.

## Tests performed

- **28 automated Python tests:** closed-form perpetuity and Gordon-growth identities, scenario outputs, payout scaling, discount/FX direction, later-year changes, zero payouts, invalid/missing/non-finite inputs, dataset completeness, duplicate keys, SQL denominator handling, income reconciliation and command-line operation.
- **25 workbook recalculation and boundary checks:** all KSPI cases and their sensitivity centres; year-five driver edits; invalid scenario names; blank active versus unselected inputs; zero dividends; invalid FX/tax/discount inputs; both Unilever WACC modes; invalid weights and terminal-growth assumptions; restoration of original baseline results.
- **81 KSPI saved input/value comparisons** against the Python implementation, including all scenario assumptions and annual cash flows.
- **98 Unilever saved formula-value comparisons** against independent DCF, equity-bridge, sensitivity-grid and residual-income calculations.
- Saved XLSX files contain no cached formula errors, macros or external-workbook dependencies. Public source hyperlinks are retained.

The Python tests ran on Linux with Python 3.12.14. The code targets Python 3.10+. No third-party installation or API credentials are required.

## What changed

The analysis now accepts legitimate custom assumptions. Baseline regression checking is an explicit option. Invalid inputs raise descriptive errors. Financial controls remain active under Python's optimisation flag. The SQL requires a complete two-year panel and returns an undefined value for growth from non-positive prior income.

Excel no longer silently selects Upside for an unknown case. Missing selected assumptions are rejected; an unused blank case does not block a valid selected case. Zero payout produces zero dividend value. Unilever rejects invalid model weights, WACC selection and discount/terminal-growth combinations. Its blended result is labelled a weighted scenario, reflecting the illustrative weights and remaining methodological limits.

## Limits of these checks

The workbook recalculation checks used the generation engine. Desktop Excel, LibreOffice, Windows/macOS execution and live browser/download behaviour were not tested. The supplied Python workbook verifiers read saved values; they do not execute Excel formulas. Recalculate and save in Excel after editing before comparing outputs.

Arithmetic correctness does not establish a current investment recommendation. KSPI discount rates, dividend paths and earnings multiple remain illustrative; the model lacks a capital/distributable-cash forecast. Unilever peer inputs, equity-bridge conventions and simplified residual-income economics require further analytical work. The other academic projects have not been source-reviewed.

These checks are reproducible internal validation, not an independent audit or proof of the portfolio owner's unaided coding ability.
