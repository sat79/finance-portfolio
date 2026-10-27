# No-API research and manual-synthesis handover — 26 October 2026

**Ready for a supervised three-company research/manual-synthesis walkthrough.** Search, retrieval, deterministic financial analysis, evidence inspection and downloads work with synthesis disabled. Actual provider-generated output and public deployment remain unverified; neither is implied by the Codex sample.

## Access the work

| Company | Readable report | Full evidence | Compact manual export |
|---|---|---|---|
| Kaspi.kz | [Report](KSPI-report.md) | [Research ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/KSPI-research.zip) | [Manual ChatGPT ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/KSPI-manual-synthesis.zip) |
| Apple | [Report](AAPL-report.md) | [Research ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/AAPL-research.zip) | [Manual ChatGPT ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/AAPL-manual-synthesis.zip) |
| Microsoft | [Report](MSFT-report.md) | [Research ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/MSFT-research.zip) | [Manual ChatGPT ZIP](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/MSFT-manual-synthesis.zip) |

[Read the Codex-generated Kaspi sample](sample/analysis.md), [initial structured result](sample/initial-result.json), [first validation](sample/initial-validation.json), [human review](sample/evaluation.md), [exact citation audit](sample/citation-audit.json), [download the sample and its supplied evidence](https://github.com/sat79/finance-portfolio/raw/refs/heads/feat/finsight-research-mvp/ai-financial-research-assistant/docs/review-artifacts/2026-10-26-no-api/codex-evaluation-sample.zip).

To use the app in the prepared workspace, run `bash scripts/start.sh` from `ai-financial-research-assistant` with the existing local SEC identification. Keep `FINSIGHT_ENABLE_MODEL=0`. Follow the [research guide](../../research-guide.md): company name → entity confirmation → research → coverage/report → citations → downloads. There is no new public deployment URL. After a code update, restart a running app to ensure imported modules are refreshed.

The new **Download compact evidence for manual ChatGPT use** button exports the existing selector's `evidence.json`, synthesis instructions and a short guide. Extract the ZIP, attach the evidence in your own ChatGPT conversation and paste the instructions. Export makes no model call. It adds no chat connection or response-import system; manual chat output remains separate and requires review.

## Verified workflow and concrete fix

Final fresh browser runs on **26 October, 15:56–15:58 GMT** passed all three companies, including Markdown, full ZIP/XLSX and compact manual-pack downloads. All successful source requests were uncached. No source request failed in these runs. The [browser record](browser-acceptance.json), [final source/quote/date audit](final-live-audit.json) and [representative live financial-source link checks](source-link-checks.json) distinguish retrieval from extraction and analytical coverage. Delivered reports/citations/model evidence match final code; manual packets match the existing compact selector exactly.

| Company | Official documents read | Annual observations | Independent original text | Retrieval/extraction time | Overall |
|---|---:|---:|---|---:|---|
| Apple | 16/16 | 40 | One selected article | 22.2s | Partial |
| Microsoft | 8/8 | 40 | One selected article | 15.3s | Partial |
| Kaspi.kz | 21/21 | 27 | Feed retrieved, no matching article | 29.3s | Partial |

All three remain partial because table layouts, omissions and unsupported coverage are still explicit. Kaspi also lacks independent article text. Successful retrieval is not complete financial analysis, exhaustive news coverage or independent verification. Annual/interim periods, reporting units and financial-group cautions remain unchanged.

A submitted new search already cleared the old report, including failed/empty searches. A new regression reproduced a narrower defect: selecting a different legal entity within the current search results still showed the previous company's report. That transition now clears the report and optional narrative before rendering. [Initial failing test](initial-workflow-regressions.txt) is retained; all new search/entity tests now pass.

The first manual-download browser run timed out waiting for the new control in an already-running app process. Its [failure record](initial-manual-export-browser-failure.txt) is retained. Restarting that app with final code and a fresh cache resolved it; the final three journeys passed. This is separate from the successful initial source-validation run and from the Codex sample validation.

## Codex sample assessment

The sample was authored in the current Codex conversation using only the **existing 25 October compact Kaspi packet**, not the fresh 26 October reports. Its initial output was saved before validation and remains unchanged. The existing validator passed **five supported paragraphs and three exact quantitative records** on the first attempt: no validation failures and no corrected replacement. Provider usage, latency and cost are null; this is explicitly **not an application-provider response**.

Human self-review: **7/8**. It identifies profit conversion, e-commerce activity/monetisation, restructured-loan risk and useful follow-up questions. Deduct one for omitting the supplied dividend proposal from the distribution discussion. Exact citations and annual calculation fields pass; no quantified causal bridge or total NPL ratio is invented. Causal relevance and materiality still require human review. The validator does not provide automated semantic verification. The schema's raw exact numerical records are auditable but less readable than rounded analyst prose.

## Gemini decision and remaining limits

[One provisional Gemini option and the minimum adapter change](gemini-decision.md). Fresh attempts to read Google's pricing, models, lifecycle, quotas and regional eligibility pages were blocked with proxy CONNECT 403. The provisional historical candidate is Gemini 2.5 Flash-Lite, **not a verified current recommendation**. Current free-tier eligibility, availability and numeric quotas remain unknown. Permit only the documentation host `ai.google.dev` through supported settings to finish that review; do not add a provider endpoint or enable billing merely to read documentation.

No Gemini adapter was added, and no OpenAI or Gemini model API call was made. The existing OpenAI path, exact numerical/citation rules, one-request limit and spending controls remain intact. Setting a local rate to zero cannot establish free-tier eligibility.

**Launch verdict:** no remaining blocker was found for the tested supervised no-API walkthrough. Automatic provider synthesis still needs an eligible configured account and an authorised, reviewed actual output. Public deployment has not been undertaken or validated. Known table/news/causal gaps must remain prominent; this is not unattended investment analysis.

## Next three actions

1. **Review the reports and sample, including the omitted dividend proposal — 20–30 minutes.** Assumes a reviewer uses the linked evidence and checks proposal versus approval/payment status; no new source is presumed.
2. **Finish the provider decision — 30–60 minutes after official documentation access is available.** Confirm maintained model, region/project eligibility, data terms and actual free quota before choosing Gemini; retain the existing OpenAI option. No billing or model request is required for this decision.
3. **Run one explicitly authorised provider acceptance — 1–2 hours for the existing OpenAI path, or 2–4 hours if a verified Gemini free-only adapter is chosen.** Assumes credentials and quota are available. Preserve the first response/failure, apply the validator and human rubric, record real usage/latency, and verify the downloaded output. No automatic retry or paid fallback.

**Checks:** 226 tests pass; Ruff lint/formatting and dependency consistency pass. No company expansion, valuation, model calls, billing changes, merge or deployment occurred.
