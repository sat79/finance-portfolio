# Supervised three-company MVP acceptance — 25 October 2026

**The deterministic demo works; the application-provider synthesis acceptance remains blocked.** All three fresh production-browser journeys pass search, entity confirmation, uncached retrieval, opening coverage, report review, citation inspection and ZIP/XLSX download. No paid call or application-generated analysis is claimed. The earlier assistant-written Kaspi brief remains a separate exercise.

| Company | Readable report | Evidence bundle | Opening coverage |
|---|---|---|---|
| Kaspi.kz | [Report](KSPI-report.md) | [Download ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-mvp/KSPI-research.zip) | [Screenshot](KSPI-coverage.png) |
| Apple | [Report](AAPL-report.md) | [Download ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-mvp/AAPL-research.zip) | [Screenshot](AAPL-coverage.png) |
| Microsoft | [Report](MSFT-report.md) | [Download ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-25-mvp/MSFT-research.zip) | [Screenshot](MSFT-coverage.png) |

## Coverage and selection

The opening report and UI distinguish successful official-document retrieval, annual financial extraction, structural table evidence and independent-news content. Known unsupported/ambiguous tables, budget omissions and unassessed structural coverage now make the research outcome partial. Counts describe selected recent disclosures and parser candidates, not every financial table in the company’s filings. Supported cells are not normalized financial observations or eligible model claims.

Only two selection rules changed: common operating-cash labels now include “Net cash from operations”; supported financial/segment tables rank before existing budgets. There is no increase to the four-table, twelve-row, eight-value or 96 KiB limits. Ambiguous relationships still abstain; complex column-oriented reconciliations remain unsupported. Headings, units, periods, cell positions and citation IDs are preserved.

[Frozen-target follow-up](table-followup.json): Apple retains its four table targets and unchanged prose targets (**8/8**); the original **4/8** artifact is untouched. Microsoft improves from the retained **2/5** checkpoint to **4/5**: `H1:T7:R26` retains operating cash and `H1:T8:R10` retains Intelligent Cloud segment revenue. Inspect the JSON for exact row IDs, cells, headers and source hashes. Constant-currency reconciliation remains unsupported. This is a recheck of known targets, not another unused-disclosure evaluation or a general accuracy estimate. Current Microsoft disclosures still have unsupported layouts; historical improvement does not imply complete current segment coverage.

## Provider pilot: prepared, not executed

[Exact candidate request](pilot/request.json), [request/estimate manifest](pilot/manifest.json), [actual access failures](provider-access.json), [evaluation checklist](pilot/evaluation.md).

The candidate is `gpt-4.1-mini` through the existing Responses API integration, using JSON-object output, `store=false`, no tools and at most 1,200 output tokens. Current model/account compatibility and pricing are **not verified**: direct no-cost requests to OpenAI pricing, model documentation and API hosts all failed with proxy CONNECT 403. The process and local configuration contain no API key. Do not treat the planning scenario as a current quote.

The manifest binds the request to its exact evidence bytes and SHA-256. At the **unverified illustrative rates** of $0.40/M input and $1.60/M output tokens, its byte-based conservative allowance gives an approximately **$0.087** reservation. Proposed fixed cap: **$0.25 total, one request, zero automatic retries**. Actual token usage, provider latency and output are null because no generation occurred; actual paid calls and spend are zero. Prices must be verified and the request re-estimated before explicit spending approval. The integration now logs latency, usage, raw output and validation/transport failures while retaining reservations. Exact numerical binding and exclusion of all structural/unsupported table claims remain enforced.

The saved environment draft preserves existing source hosts and adds only `openai.com`, `developers.openai.com`, `api.openai.com`, plus a secure `FINSIGHT_OPENAI_API_KEY` binding scoped to the API host. `OPENAI_` is reserved for managed bindings; the conventional local variable remains supported. **Next action: review/save these settings, enter the API key securely, and publish the environment.** Saving the draft did not apply or publish it. Then retest access, verify official prices/model availability, and present the exact single-call charge for authorization. Keep `FINSIGHT_ENABLE_MODEL=0` until that approval.

## Demo and verification

Start the app using the existing research guide. Enter Apple, Microsoft or Kaspi.kz; confirm the entity; refresh evidence; review the opening coverage; inspect Key findings and dated table cells; open **Evidence & coverage → Inspect citation register**; download the complete evidence bundle. For the later authorized Kaspi request, open **Optional model narrative**, review the estimate and approve the single request. Accepted output is labelled **Application-generated analysis — human review required** and can be downloaded with the evidence in a combined ZIP. That final provider step has only synthetic no-cost integration coverage so far; it is not demonstrated live.

**219 tests pass**, plus Ruff lint/formatting and dependency consistency. Targeted tests cover label recognition, relevance-before-budget ranking, abstention, opening coverage, proxy-secret compatibility, exact input estimation, one-request enforcement, timeout/incomplete/invalid-response audits, and the approval → generated-output → combined-download UI path with a synthetic provider. Existing wrong-metric/year/currency/source, unrelated-citation, financial-group and spending regressions still pass. Synthetic output is never used as evidence of model quality.

[Fresh browser acceptance](browser-acceptance.json) records exact cutoffs, stage latencies, successful uncached requests and source failures. Official documents are 16/16 Apple, 8/8 Microsoft and 21/21 Kaspi; annual observations 40, 40 and 27. Apple and Microsoft each have one independent original with cited text. Kaspi’s publisher feed was retrieved but yielded no matching article; it still has no independent article text. Table gaps remain prominent for all three.

**Recommendation:** continue supervised deterministic demonstrations. Hold MVP-completion, merge and deployment approval until the one real application-provider output is obtained and reviewed under the four-part rubric. No merge, deployment, valuation or company expansion occurred.
