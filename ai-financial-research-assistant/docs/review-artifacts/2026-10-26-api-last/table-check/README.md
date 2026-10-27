# Material evidence gaps and bounded check

Two narrow changes were made: recognise the explicit heading **SEGMENT RESULTS** before applying the existing table budget, and retain **at most one already retrieved independent original article** in the compact packet alongside official evidence. No universal parser, new publisher route, numeric normalisation or company coverage was added. Four tables, twelve rows per table, eight values per row and the 96 KiB cap remain unchanged.

## Why these gaps matter

| Gap | Analytical consequence | Action / remaining boundary |
|---|---|---|
| Supported Microsoft segment table lost to comprehensive-income table | Reader could see group results but miss comparable segment revenue and operating income | Added the literal common heading to ranking. Source row, column, date, units and section records are retained. This does not infer segment scope from flattened numbers or make tables eligible model claims. |
| Read Apple/MSFT original articles absent from compact packet | Manual/provider synthesis could omit a material leadership development or a policy/regulatory discussion that the full report already exposed | Keep one read Guardian article with metadata, exact support and provenance. Discovery-only records remain excluded from claim support. These articles do not quantify financial impact. |
| Microsoft GAAP/non-GAAP and currency reconciliations | Cannot automate a recurring-earnings or FX contribution bridge | Remain unsupported when units/layout are ambiguous. The selected prose describes the relevant measures but is not a reconstructed reconciliation. |
| Kaspi credit stock without exposure/provision/recovery/capital bridge | Cannot calculate an NPL rate, loss coverage, bank capital headroom or sustainable distributions | Keep the exact Stage 3 subset quote and the dividend proposal question. Do not infer approval/payment. Relevant independent Kaspi news remains unavailable through the reviewed route. |
| Apple table/row budget, product/Services and regional evidence omissions | Cannot fully explain mix, cash conversion or regional demand | Preserve disclosed margin explanations and structural evidence where supported; keep missing contribution analysis explicit. No annual substitution. |

Priorities for a future evidence-only pass: first an audited credit/capital bridge for Kaspi if the source supplies one; then a single reviewed Microsoft cash/investment reconciliation. Those are proposed investigations, not implemented claims or authorisation to build a general parser. Current table records remain human-review material rather than normalized quantitative evidence supplied to the model.

## Previously unused disclosure: Microsoft, 28 January 2026

[Original SEC release](https://www.sec.gov/Archives/edgar/data/789019/000119312526027198/msft-ex99_1.htm), FY2026 second quarter. The source has separate three-month and six-month header bands for December 31, with 2025/2024 columns and an explicit millions label. This differs from the earlier fiscal-year-end three/twelve-month check and the Apple benchmark. It shares the issuer's segment-table convention, so this is a limited generalisation check, not evidence of arbitrary-layout support.

The URL was absent from the earlier review archives. It was retrieved fresh through the existing bounded SEC route; exact retrieval time, source hash and access record are in [preregistered.json](preregistered.json), and original HTML is in [original-source.zip](original-source.zip). Five targets were fixed from raw-source inspection **before running the selector and before changing its rules**. Source ordinals below are review locators only; none is hardcoded in application selection.

| Fixed target | Before | After |
|---|---|---|
| Group net income, quarter and six months (T5 R36) | Supported | Supported |
| Net cash from operations, quarter and six months (T8 R26) | Supported | Supported |
| Productivity and Business Processes revenue (T9 R9) | Omitted by table budget | Supported |
| Intelligent Cloud operating income (T9 R24) | Omitted by table budget | Supported |
| GAAP/non-GAAP adjustment bridge (T1) | Unsupported column-oriented layout | Still unsupported |

**2/5 → 4/5** on these fixed targets. [Before](before.json) and [after](after.json) preserve selected cells, headers, units, context and diagnostics. No tuning followed the after-result. Source-cell alignment does not establish that every contextual financial interpretation is correct.

**Tradeoff:** the after-result omits comprehensive income T6 by count and balance sheet T7 by the unchanged 96 KiB byte budget. That worsens coverage outside the five targets; the score does not mean complete disclosure coverage. The report’s coverage register exposes these omissions. Adding unsupported reconciliation claims to improve the score would be incorrect.

The original frozen Apple **4/8** result remains untouched. Earlier prose-plus-table follow-up remains **8/8**; the recheck confirms all four table targets remain supported. The earlier Microsoft original **2/5** and later **4/5** records also remain untouched; its four supported targets still pass. See [original-benchmarks-recheck.json](original-benchmarks-recheck.json). These historical checks are replayed saved bytes, not fresh source retrievals.
