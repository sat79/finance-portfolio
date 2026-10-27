# Application-provider synthesis evaluation — pending real output

This is the evaluation plan for the exact request in [request.json](request.json), not a completed model evaluation. The earlier [assistant-produced brief and self-review](../../2026-10-25-tables/kspi-exercise-evaluation.md) are separate and cannot satisfy this acceptance gate.

| Dimension | Maximum | Required evidence for full credit | Actual result |
|---|---:|---|---|
| Prioritisation | 2 | At most three useful material findings; balances profitability, operating drivers and financial/credit risk where supported; at most two focused questions; no generic filler | Not evaluated |
| Factual support | 2 | Every cited quote is present in the supplied citation; each numerical record exactly matches metric, value, period, currency, unit and sources; an analyst checks that the source actually supports the interpretation | Not evaluated |
| Period/scope consistency | 2 | Annual baseline stays separate from quarterly/YTD; reported vs constant-currency, group vs parent profit, EBITDA vs IFRS and Kaspi financial-group limitations remain explicit | Not evaluated |
| Unsupported causation | 2 | Management explanations remain attributed verbatim; interpretations stay unverified; concurrent changes do not become invented causes, contribution estimates or forecasts | Not evaluated |

Score and deductions: **not assigned**. Proposed acceptance gate remains at least 7/8, no zero dimensions, and no hard failure. Record an explicit deduction for an omitted material contrast even if other prose is polished. An unsupported numerical claim, mismatched source/period/currency, invented citation or table-based assertion is a hard failure. Structural table data is present for transparent coverage but is ineligible for this provider's prose and numerical claim records.

After the single authorized request:

1. Preserve request hash, evidence hash/cutoff, provider response ID, raw response text, status, usage and measured latency. Record all HTTP, timeout, incomplete-output, JSON and validation failures. Never retry automatically; retain the spending reservation even after failure.
2. Run the application validator. For each accepted quantitative record, compare every field with `quantitative_evidence`; for each paragraph, show exact support excerpts and citation IDs. A valid reference and copied excerpt alone are not semantic verification.
3. Manually trace each interpretation to the cited metric/document, nearby heading, reporting period and scope. Check annual/interim mismatch, company vs independent source, acquisition/FX/IAS29 effects, group vs parent, and whether cash flow is being misrepresented as distributable cash. Keep Kaspi's absent independent-news corroboration prominent.
4. Score all four dimensions, state deductions and unresolved questions, and label the result **application-generated output**. Export output plus evidence, not a replacement assistant-written answer. If rejected, publish the failure and deterministic report with no claim of synthesis success.

Actual application-provider calls: **0**. Actual usage and latency: **unavailable**. Paid spend: **$0**. No output exists to score. Six synthetic provider/UI tests validate the integration mechanics only; they do not evaluate model behaviour.
