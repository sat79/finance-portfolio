# Verification scope
14 September 2026. Checks performed on the distributed portfolio files using Python 3.12 on Linux.

| Project | Tests passed | Additional checks |
|---|---:|---|
| KSPI | 28 | 81 saved workbook comparisons; scenario reference outputs |
| Unilever | 4 | 98 saved formula values independently reproduced |
| Consumer lending | 10 | Full synthetic analysis run; affordability and stress controls |
| Market risk | 11 | Full analysis rerun matches saved results |
| Econometrics | 5 | Full analysis rerun matches saved results |
| AURA | 5 | Full analysis rerun matches saved results |

**Total: 63 passing tests.** The three scientific analyses match distributed JSON results with relative tolerance 1e-7 and absolute tolerance 1e-9. Numerical dependencies match the pinned direct versions; the shared runtime supplies supporting libraries. Each project has a refreshed checksum manifest.

Excel theme-name metadata was relabelled. All other ZIP entries, including cells, formulas and style definitions, were byte-identical before and after that metadata edit. The spreadsheet checks use saved values; desktop Excel recalculation was not tested in this release.

Checks validate defined calculations and controls, not source accuracy, external model validity or future performance. The lending data are wholly synthetic. Risk backtests reject nominal coverage, macro data contain revision hindsight, and AURA remains empirically unvalidated.

The repository's portable runner checks structure, manifests and the three standard-library financial projects. Follow the other project READMEs for numerical dependencies and full analyses. The market CSV is reconstructed from the documented arch dependency and excluded from distribution.
