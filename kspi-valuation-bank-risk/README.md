# Kaspi.kz valuation and bank risk

**Financial question:** how do distributions, currency translation and lending economics affect equity value?

An independent finance portfolio study for Satvik Sahni. Financial assumptions dated 11 September 2026; calculation review 12 September 2026.

## Start with the evidence

- [Super-app and Türkiye thesis](reports/Super-App-and-Turkiye-Thesis.md): evidence for the established business, expansion milestones and valuation implications. Updated 13 September 2026.
- [Geographic earnings bridge](reports/geography-results.json), with [reproducible code](src/analyse_geography.py).
- [Investment memo](reports/Investment-Memo.md): question, conclusions, assumptions and limitations.
- [Editable Excel model](models/KSPI-Valuation-and-Bank-Risk.xlsx).
- [Sources and definitions](data/SOURCES.md).
- [Validation report](reports/Validation.md) and [results with annual cash flows](reports/results.json).
- [Python calculations](src/analyse.py), [SQL analysis](sql/segment_analysis.sql) and [tests](tests/test_analysis.py).

## Run from a downloaded copy

Extract the archive. Open a terminal inside `kspi-valuation-bank-risk`. Use Python 3.10 or newer; no third-party packages, credentials or network access are needed. Tested on Linux with Python 3.12.14. On Windows, use `py` instead of `python3` if appropriate for your installation.

```bash
python3 src/verify_package.py
python3 -m unittest discover -s tests -v
python3 src/analyse.py --verify-reference
python3 src/verify_workbook.py
python3 src/analyse_geography.py
```

Expected baseline: Base **$73.11**, Downside **$45.53**, Upside **$95.68** per ADS. These are conditional model outputs, not price targets. The earnings sensitivity is KZT113.25bn after tax under the supplied shocks.

The test suite reports 28 tests. The workbook verifier compares 81 saved values/inputs. It does **not** run Excel or prove that an edited workbook has recalculated.

## Change assumptions

Copy `data/assumptions.json` to `my-assumptions.json`, edit the copied numeric inputs, and run:

```bash
python3 src/analyse.py --assumptions my-assumptions.json --output reports/my-results.json
```

Do not use `--verify-reference` for deliberately changed assumptions: it checks the distributed baseline. Python JSON inputs and Excel inputs are separate; changes do not synchronise automatically. Update matching inputs, recalculate and save Excel, then compare the resulting cash-flow schedules. The shipped workbook verifier uses `data/assumptions.json`.

In Excel, select exactly Base, Downside or Upside in `Assumptions!D4`. Blue numeric cells are editable. Missing/invalid selected inputs produce `#N/A`; a zero dividend is allowed. Cash flows are five end-year annual periods. Quarterly payment timing is approximated by annual year-end payments.

## Data controls and scope

`segments.csv` is a six-row extracted dataset, not a production-scale data pipeline. Its key is year plus segment. Both years must contain Payments, Marketplace and Fintech and reconcile to `group_income_controls.json`. The SQL reports consolidated-scope segment growth, not organic growth; it returns null where a percentage is not meaningful.

The model does not forecast bank regulatory capital or sustainable payout capacity. Rates, growth paths, FX paths and P/E are assumptions, not calibrated market estimates. The static earnings sensitivity is not IFRS 9 ECL. See the memo before interpreting the output.

`SHA256SUMS.txt` detects accidental modification of distributed files. It is not a signed authenticity guarantee. Intentional edits will fail that check. No open-source licence has been assigned; third-party financial data remains subject to its source terms.
