# Previously unused disclosure check — frozen before presentation edits

**Document:** [Apple fiscal 2025 Q2 results, published 1 May 2025](https://www.sec.gov/Archives/edgar/data/320193/000032019325000055/a8-kex991q2202503292025.htm), quarter ended 29 March 2025. This is a historical disclosure freshly retrieved on 25 October, not a newly published release or a fresh Apple research report.

The URL was absent from the three 24 October research bundles and tracked content at `25b142e`. It was outside the 11-passage development benchmark. Discovery used SEC submissions → the 1 May 8-K → its linked exhibit, through existing bounded clients with `refresh=True`. Actual successful requests, retrieval timestamps and source hashes are recorded in [discovery](discovery.json), [filing discovery](filing-discovery.json) and [retrieval](retrieval.json). Policy configuration alone was not treated as proof of access.

The document was read manually first. Eight target evidence groups were recorded in [preregistered-targets.json](preregistered-targets.json) before running the selector. [frozen-result.json](frozen-result.json) records the subsequent result, timestamps, selected block IDs and selector hash. **No selection rule was changed before or after this check.** The same hash is retained in this update. This single manually chosen disclosure is an additional check, not a randomized test or general accuracy estimate.

| Reviewed evidence | Original blocks | Outcome |
|---|---|---|
| Quarterly revenue and EPS, with period | `H1:B6` | Selected |
| CEO Services/product discussion | `H1:B7` | Selected as drivers; includes promotional wording, not independently verified facts |
| CFO quarterly operating cash/returns and installed-base statement | `H1:B8` | Selected as drivers; this category does not itself validate materiality or causation |
| Dividend and repurchase authorization | `H1:B9` | Selected as capital; authorization is not execution |
| Services quarterly/YTD numerical revenue | `H1:B37` plus table period/unit headers | Omitted |
| Greater China quarterly/YTD revenue | `H1:B77–78` plus table period/unit headers | Omitted |
| Group quarterly/YTD net income | `H1:B60–61` plus table period/unit headers | Omitted |
| Six-month operating cash flow | `H1:B185` plus cash-flow period/unit headers | Omitted |

**Result: four of eight reviewed evidence groups fully selected.** All four prose targets were retained; all four table targets were omitted. The parsed table headings, dates, metric names and values are split across blocks and the current selector does not reconstruct table relationships. For example, quarterly cash generation in the CFO paragraph is retained while the six-month cash-flow statement is not; neither should substitute for the other. Revenue/EPS alone also omits a direct net-income comparison.

The complete extracted source is [document.json](document.json), including every block's original locator and heading. Omissions are deliberately left visible; no rule was tuned to make this check pass. This strengthens the case for human review of the full appendix before synthesis, and limits claims about general selection quality.
