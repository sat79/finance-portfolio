# FinSight: table evidence and completed synthesis — 25 October 2026

**Ready for a supervised three-company demo, with omissions displayed up front.** The demo can now show company-name research, current reports with readable financial rows, original citations and evidence downloads, plus a completed, reviewed Kaspi synthesis exercise. It cannot claim comprehensive table coverage, automated semantic verification or application-generated synthesis. Reviewed company coverage remains Apple, Microsoft and Kaspi.kz.

| Company | Complete updated report | Complete evidence download | Table screenshot |
|---|---|---|---|
| Kaspi.kz | [Report](KSPI-report.md) | [ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-tables/KSPI-research.zip) | [View](KSPI-tables.png) |
| Apple | [Report](AAPL-report.md) | [ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-tables/AAPL-research.zip) | [View](AAPL-tables.png) |
| Microsoft | [Report](MSFT-report.md) | [ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-tables/MSFT-research.zip) | [View](MSFT-tables.png) |

**Completed exercise:** [256-word Kaspi brief](kspi-completed-brief.md), [four-part evaluation with deduction](kspi-exercise-evaluation.md), [exact citation/calculation audit](kspi-exercise-citation-checks.json). This is assistant-produced work in this session, not output from the application's model provider. It uses only the previously supplied **24 October evidence**, not the later fresh research. Self-assessed **7/8**, with one prioritisation deduction for omitting the available Fintech growth/profit contrast. No paid API call was made.

## What changed

HTML financial rows now retain original `td`/`th` cell text, `rowspan`/`colspan`, table/row/cell ordinals and source tag positions (one-based line, zero-based character offset in decoded HTML). Header paths must structurally cover each value cell. Dates, literal quarterly/YTD/instant headings, nearby statement/segment context and explicit unit headings stay attached. A preceding row heading is context, not inferred segment membership. Existing B-citation ordinals are untouched; table citations use separate `T`/`R` IDs with URL, retrieval timestamp and source hash.

The reader sees compact grids only where column-header paths match exactly. Report and optional model evidence refer to the same structural records; row citations reference their parent table instead of duplicating it. These records are **not normalized financial facts** and are ineligible for free-prose or numerical model claims. Existing financial observations, deterministic calculations, period/currency/source checks and Kaspi financial-group controls remain unchanged. Currency codes, missing values, annual substitutes and table arithmetic are not inferred.

Bounds per source document: inspect at most 200 HTML tables; parse at most 500 rows/40 physical columns per table; retain at most four candidate tables, 12 selected rows per table, eight values per row, 12 header rows and **96 KiB** of structural evidence. Omitted rows/tables and unsupported layouts are labelled. PDF or old flattened snapshots are not reconstructed into tables. Full original documents and available structured records remain in the appendix/export.

## Evidence of usefulness and limits

The [table comparison](table-checks/README.md) retains the original frozen Apple **4/8** result, shows **8/8** on those same reviewed groups with table context now preserved, and records **2/5** on an additional previously unused Microsoft disclosure with a different layout. Source HTML, targets registered before execution, the first Microsoft checkpoint and exact outcomes are supplied. These small checks are not general accuracy estimates.

Fresh production-browser runs on **25 October, 11:02–11:03 UTC/GMT** passed name search → entity confirmation → uncached retrieval → report/table review → citation register → ZIP/XLSX download. The [acceptance record](browser-acceptance.json) and [manifest](manifest.json) give cutoffs, actual requests, hashes and table status counts. Downloaded reports match final rendering byte for byte, and a final parser check against the same original source bytes preserves every delivered table. An initial citation-inspector check exceeded the test's five-second wait; it passed with a bounded 30-second wait. No source failure was hidden or replaced with replay.

| Company | Official documents | Annual observations | Independent news | Recent table records |
|---|---:|---:|---|---|
| Apple | 16/16 | 40 | One original article with cited text | 7 structured tables, 31 rows |
| Microsoft | 8/8 | 40 | One original article with cited text | 4 structured tables, 20 rows; 1 unsupported IR table |
| Kaspi.kz | 21/21 | 27 | Feed retrieved; no matching article — **partial** | 4 interim tables: 9 structured rows and 5 explicitly ambiguous rows; no selected earnings-release table |

**207 tests pass**, including 11 targeted table tests; lint, formatting and dependency consistency pass. Regressions cover merged cells, quarterly/YTD dates, units, original positions, malformed/nested/ambiguous layouts, month-word matching, budget limits, old-snapshot abstention, report/model/export parity and rejection of unsupported table prose claims. Existing safeguards continue to pass.

## Demo boundary and next action

Proceed with a **supervised walkthrough of these three linked reports**, using the completed Kaspi brief as an explicitly assistant-produced example. Show missing table coverage and Kaspi independent-news limitations before drawing conclusions. Reviewers can inspect full source evidence for omitted rows. Do not describe the exercise score as independent validation, or the new structural mappings as a completed quarterly extraction/semantic-verification system.

Remaining work is visible: cash-row vocabulary, table prioritisation, column-oriented reconciliations, PDF layouts, incomplete Kaspi table context, comparable-scope/causal bridges and independent news. Those gaps prevent unattended or exhaustive research claims. Paid model calls remain disabled; no company coverage expansion, valuation, merge or deployment occurred.
