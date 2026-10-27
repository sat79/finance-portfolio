# FinSight: API-last review handover

The no-API company-name → confirmed entity → sources → cited financial report → download workflow is usable for **AAPL, MSFT and KSPI**. The branch is `feat/finsight-research-mvp`, [PR #1](https://github.com/sat79/finance-portfolio/pull/1). API setup remains deferred. No external model call, credential request, billing activation, merge or deployment was performed.

## Read and download

These are complete reports and bundles downloaded through the production app, not reconstructed fixtures. Manual samples are explicitly separate from application output.

| Company | Readable report | Complete evidence + workbook | Compact evidence for manual use | Manual Codex sample and assessment | Download sample + supplied evidence + validation |
|---|---|---|---|---|---|
| Apple | [Report](AAPL-report.md) | [ZIP](AAPL-research.zip) | [ZIP](AAPL-manual-synthesis.zip) | [Sample](samples/AAPL/analysis.md) · [Review](samples/AAPL/evaluation.md) | [ZIP](AAPL-manual-evaluation.zip) |
| Microsoft | [Report](MSFT-report.md) | [ZIP](MSFT-research.zip) | [ZIP](MSFT-manual-synthesis.zip) | [Sample](samples/MSFT/analysis.md) · [Review](samples/MSFT/evaluation.md) | [ZIP](MSFT-manual-evaluation.zip) |
| Kaspi.kz | [Report](KSPI-report.md) | [ZIP](KSPI-research.zip) | [ZIP](KSPI-manual-synthesis.zip) | [Separate revision](samples/KSPI/analysis.md) · [Review](samples/KSPI/evaluation.md) | [ZIP](KSPI-manual-evaluation.zip) |

The research ZIP contains Markdown, the complete evidence snapshot, source/citation register, coverage, financial workbook and full selected model evidence. Its download has been compared with the standalone report. The compact pack retains the eligible subset and instructions. The appendix remains complete even where the opening is abbreviated.

## What changed

- **Shared preparation:** UI estimate, configured manual request export, pilot script and eventual execution use the same compact evidence/configuration. Defaults are 2,400 output tokens, explicit `none` reasoning and one request. Exact request SHA-256 binds approval to its contents; changing settings resets approval and a mismatched hash is rejected before budget reservation. Offline tests compare actual payload bytes across these paths using a stub transport, without credentials or a model call. Citation eligibility, exact numeric binding, persistent reservations and no automatic retries remain intact.
- **Readable opening:** business description, latest reported change, supported driver/explanation, risk coverage and missing evidence precede the full appendix. Apple now exposes revenue and the product-margin explanation rather than only the announcement date. Microsoft’s generic risk boilerplate is explicitly insufficient for a specific risk assessment. Displayed annual percentages are rounded; exact underlying records remain unchanged. Annual, quarterly and YTD periods remain distinct; no causal bridge is manufactured.
- **Bounded material evidence fixes:** the common “SEGMENT RESULTS” heading is prioritised before existing budgets; compact evidence now retains one already retrieved independent original article. Apple/MSFT move from zero to one independent article in compact evidence; Kaspi stays zero. No new publisher route or broader parser was added.

[Offline preparation checks](offline-preparation-check.json) show downloaded compact evidence equals shared preparation for each company. Recorded pricing was used only for an offline comparison; availability, deprecation and prices were **not reverified in this task**. These estimates do not authorize execution. Without nonsecret model settings, the manual ZIP still works and contains evidence/instructions; with them it additionally contains the exact request and preparation manifest.

## Personally verified workflow, recorded times

The final fresh browser run was recorded **26 October 2026, 18:04–18:06 UTC**. It used the real local launcher and refreshed source requests. These dates are retained as recorded evidence; they are not a claim of a new 27 October retrieval.

| Company | Registered official documents read | Annual observations | Retrieved independent original articles | Source access failures | Retrieval/extraction time | Outcome |
|---|---:|---:|---:|---:|---:|---|
| AAPL | 16/16 | 40 | 1 | 0 | 22.446s | Partial |
| MSFT | 8/8 | 40 | 1 | 0 | 14.594s | Partial |
| KSPI | 21/21 | 27 | 0 | 0 | 28.716s | Partial |

[Browser audit](summary.json) records exact cutoffs, access failures, coverage and steps. The ZIP snapshots retain per-source timestamps, URLs, hashes and `cached:false` for successful refresh requests. Name resolution, explicit entity selection for ambiguous Apple results, previous-company state clearing, citation inspection, Markdown, full ZIP and manual ZIP downloads all passed. Source access succeeded; analytical coverage is still partial. Kaspi news is **no matching readable independent article**, not a network success converted into news coverage. Discovery headlines do not supply substantive claims.

Table coverage remains visible in the opening/UI: AAPL 32 supported rows with 5 unsupported and 6 omitted tables; MSFT 27 supported rows with 17 unsupported and 2 omitted tables; KSPI 22 supported rows, 1 ambiguous row, 21 unsupported and 3 omitted tables, plus unassessed format limitations. Exact diagnostics and omitted rows remain in each bundle.

## Manual analysis evaluation

All three samples are **manual Codex output from this conversation**, not provider responses. Each initial structured result was saved before validation. Each passed the existing validator on its first run: five paragraphs, three complete quantitative records, **no initial validation failures and no corrective replacement**. Usage, provider latency and provider cost are null/not measured; no API performance is invented.

The original Kaspi [sample](../2026-10-26-no-api/sample/analysis.md) and [7/8 assessment](../2026-10-26-no-api/sample/evaluation.md) remain unchanged. The separate revision explicitly connects the dividend **proposal**, shareholder **approval** and actual **payment** question; it does not assert the later events occurred. Its bounded self-review scores 8/8. Apple and Microsoft each score 7/8, with deductions for analytical prioritisation/coverage. Their frozen supplied packets predate the independent-article compact fix; no retrospective credit is given for evidence absent from those packets.

The rubrics check prioritisation, support, period/scope and unsupported causation. Exact citation/quote/record matching is mechanical; relevance, materiality and causation still require human review. The samples identify useful drivers, earnings-quality issues and follow-up questions but do not supply a normalized cash/capital bridge.

## Generalisation and remaining gaps

[Material gap review and unused-disclosure check](table-check/README.md): five targets were fixed from a previously unused Microsoft January 2026 release before running the selector or changing rules. **2/5 → 4/5** after ranking; complex reconciliations remain unsupported. The unchanged byte budget now omits its balance sheet, a disclosed tradeoff outside the target score. Original Apple 4/8 and later benchmark records are preserved; saved-source rechecks are explicitly replay, not fresh retrieval.

Kaspi independent corroboration, credit denominator/provisions/recoveries/capital headroom and later dividend status remain missing. Apple product/Services, regional and cash-conversion explanations are incomplete. Microsoft recurring-earnings and investment/cash bridges remain incomplete. Structured tables are readable evidence for human inspection, not eligible normalized model claims. These limitations prevent unattended investment conclusions; they do not prevent a supervised evidence-first demo.

## Setup, launch and verification

Working folder: `/workspace/finance-portfolio/ai-financial-research-assistant`. The latest local service uses `http://127.0.0.1:8526` **inside this environment**; it is not a public deployment or an address accessible from your Mac. Use the exact [Intel Mac setup steps](../../mac-setup.md) to run `bash scripts/start.sh` locally, then open `http://localhost:8501` on your Mac.

[Checks](checks.json): **232 tests passed** in the existing environment and a fresh Python 3.12 Linux virtual environment; lint/format checks, dependency consistency and launcher syntax passed. The full pinned Intel macOS 12/CPython 3.12 wheel set, including the PDF parser, downloaded successfully. Native Mac installation, desktop Chrome/Excel and hosting performance remain **untested**, not inferred from Linux or wheel checks.

[Deployment requirements](../../deployment-preparation.md) and a [nonsecret environment template](../../../deploy/environment.example) are prepared. No host, container, paid resource or public endpoint was created.

## Next three actions — API last

1. **Intel Mac acceptance (30–60 minutes):** follow the guide, launch with synthesis disabled, run the three names, inspect source links and open downloaded files. Assumes Python 3.12, macOS 12+ and permitted source access; local platform failures may add time.
2. **Independent report review (45–90 minutes):** inspect the three samples and the cited gaps, including the balance-sheet selection tradeoff. Decide which missing evidence is necessary for the intended supervised demo. Assumes a reviewer comfortable with annual/interim and financial-group distinctions.
3. **Final API stage only (30–60 minutes after separate authorization/access):** verify maintained model availability/deprecation, settings and current pricing; prepare the shared compact request; approve its exact hash, estimate and one-request cap; execute once without automatic retries; retain any failure and validate actual usage, latency, citations and download. No credential is needed for steps 1–2.

**Verdict:** ready for a supervised, three-company **no-API** demo and manual analytical review. Application-provider synthesis, native Mac acceptance and a production operating setup remain unverified. Do not treat this as authorization to merge or deploy.
