# Portfolio review and recruiter priorities

Reviewed 11 September 2026. Scope: the accessible Unilever workbook and report, the website, existing README scaffolds, and the newly created KSPI study. The original risk notebooks, econometrics code and dissertation could not be located. Their quality is unassessed.

## Unilever — good foundation, material analytical qualifications

The pack contains a useful historical series, average-balance DuPont analysis, explicit FCFF forecasts, residual income and a peer cross-check. These are substantive foundations. The available files are stored as generated artifacts dated September 2026, and the report explicitly says it substantiates a CV claim. They are not evidence that these exact files were submitted during the MSc.

| Finding | Evidence | Treatment |
|---|---|---|
| Information-timing inconsistency | DCF!B5/D5 and report label 31-Dec-2024, but use FY2024 annual results | Relabelled as retrospective FY2024 exercise; removed hindsight-free claim |
| No CAPM/WACC derivation | Original DCF!B10 = 7%; RI!B9 = 7.5% hardcodes | Added optional CAPM schedule and switch; assumptions remain illustrative |
| Sensitivity headers do not control formulas | Original DCF!G33:K36 embed numeric rates | Replaced with header references and centred the grid on selected WACC/g |
| Two separate weighting calculations | Summary!D3 repeats weights from B8:B10 | Linked D3 to weighted contributions |
| Duplicated historical inputs | Summary and DCF repeat historical values | Linked relevant duplicates to Historicals |
| Terminal dependence is large | DCF!B35 / B36 is about 79.6% | Added explicit terminal-value share |
| Residual-income economics are simplified | Underlying EPS grows reported book value; terminal RI grows perpetually | Added clean-surplus and no-explicit-fade disclosures; not misrepresented as fixed |
| Peer evidence needs more work | Comps has mixed business models and dated third-party ratio URLs | Still requires date-aligned primary-source peer inputs and definitions |
| Equity bridge needs substantiation | Book NCI subtraction and weighted-average diluted shares | Explain valuation treatment and obtain valuation-date fully diluted shares |

The revised workbook is technically more inspectable. It does not convert unverified source assumptions into independently validated investment research. The old report’s rating and “explicit fade” explanation should not be circulated with the revised workbook.

