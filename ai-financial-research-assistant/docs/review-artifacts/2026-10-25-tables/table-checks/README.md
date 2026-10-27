# Table selection: original comparison and additional layout

The original Apple [frozen 4/8 result](../../2026-10-25/unused-disclosure/frozen-result.json) is unchanged. The new [comparison record](comparison.json) contains its hash, source hashes, exact selected cells/header paths and the new outcomes. [Original HTML sources](original-html-sources.zip), extracted documents and rendered single-disclosure reports are supplied for inspection. These historical releases were fetched afresh; they are not presented as the latest company results.

## Apple: four concrete table omissions addressed

Source: [1 May 2025 release](https://www.sec.gov/Archives/edgar/data/320193/000032019325000055/a8-kex991q2202503292025.htm), fiscal quarter ended 29 March 2025. The original-source hash matches the prior frozen source. Its tables use wide `colspan` groups, separate currency cells and date cells spanning multiple physical columns. The new parser preserves those relationships from HTML, independently of the old flattened B-blocks.

| Target | New citation | Column-bound values, as reported in millions | Result |
|---|---|---|---|
| Services net sales | `H1:T1:R6` | 26,645 / 23,867 for three months; 52,985 / 46,984 for six months | Retained with Net sales heading |
| Greater China net sales | `H1:T1:R35` | 16,002 / 16,372 for three months; 34,515 / 37,191 for six months | Retained with segment heading |
| Group net income | `H1:T1:R23` | 24,780 / 23,636 for three months; 61,110 / 57,552 for six months | Retained with consolidated statement title |
| Operating cash | `H1:T3:R20` | 53,887 / 62,585 for six months | Retained without substituting the quarterly CFO quote |

Each pair is headed **29 March 2025 / 30 March 2024**, not a publication date. Exact source unit wording includes share/per-share exceptions. Currency/sign cells are retained in the source-cell record; no currency code is inferred from a dollar sign. Four previously selected prose targets remain selected, giving **8/8 reviewed groups** now versus **4/8 frozen**. No normalization into the annual dataset occurred.

Remaining omissions: the row budget excludes some later product-category detail (iPhone, Mac, iPad, Wearables and a repeated Services row). It also intentionally does not select every financial row. See the [rendered disclosure report](apple-disclosure-report.md), [complete extracted document](apple-document.json) and source HTML. The 8/8 figure concerns the eight original review groups, not exhaustive financial coverage.

## Microsoft: additional, previously unused layout

Source: [30 April 2025 release](https://www.sec.gov/Archives/edgar/data/789019/000095017025061032/msft-ex99_1.htm), quarter ended 31 March 2025. The URL was absent from tracked content at `af8d058` and the prior review bundles. SEC discovery/access records are included. Its statements put month/day and years on separate header rows and include currency signs inside value cells; its constant-currency reconciliations orient financial measures across columns.

Five targets were [registered after manual source/layout inspection and before changed-selector execution](msft-preregistered.json). This is not a blind or randomized experiment. The [first evaluation checkpoint](msft-first-checkpoint.json) is retained. Later changes explicitly diagnosed more column-oriented tables and tightened month-word and indistinguishable-header validation using synthetic regressions; assertions confirm **no selected row/value mapping changed** from that first checkpoint.

| Target | Outcome | Exact evidence / remaining issue |
|---|---|---|
| Total revenue | Retained, `H1:T4:R11` | 70,066 / 61,858 for three months; 205,283 / 180,395 for nine months; units in millions, 2025/2024 columns |
| Group net income | Retained, `H1:T4:R36` | $25,824 / $21,939 for three months; $74,599 / $66,100 for nine months; exact source currency text retained |
| Operating cash, quarterly/YTD | **Omitted** | `Net cash from operations` is outside the current row-label matcher; the source's 37,044 / 31,917 / 93,515 / 81,353 row is not selected. No other cash figure is substituted. |
| Intelligent Cloud segment revenue | **Omitted** | Table 8 falls outside the four-table budget. The source row remains in the full extracted document/HTML. |
| Reported/constant-currency reconciliation | **Unsupported** | Table 1 places metrics across columns. It is explicitly rejected rather than transposed or associated with years by guessing. |

**2/5 reviewed groups retained.** Both retained statement rows preserve **Three Months Ended / Nine Months Ended**, **March 31**, **2025/2024**, units and source-cell positions. The omission result remains visible; no post-check tuning was used to make the financial targets pass. Read the [disclosure report](msft-disclosure-report.md) and [source document](msft-document.json). A supervised reviewer still needs the original tables for missing cash, segments and currency reconciliation.

The code uses structural spans and generic row categories, not these review block/table IDs. Flattened text, PDF tables, malformed spans, missing dates/units, overlapping cells, ambiguous headings and oversized layouts do not produce guessed mappings. Exact scope remains company-reported; structural alignment is not semantic or accounting verification.
