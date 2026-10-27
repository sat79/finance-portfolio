# Application synthesis preflight — 26 October 2026

**Network access now works. Credential/account availability and spending approval remain outstanding.** No application-generated output exists yet; the prior assistant-written brief is not substituted for it.

Fresh requests at 00:53 GMT retrieved official deprecation, model and pricing documentation with HTTP 200. The API host returned HTTP 401 to the model-list request. Both supported credential variables were absent from the process and local runtime configuration; no secret value was exposed. Runtime metadata still reports revision 6 and the earlier allowlist, so actual requests—not the stale status—establish network access. [Access log](access.json).

The official deprecation page confirms **GPT-4.1 mini shuts down on 14 January 2027**, and recommends **GPT-6 Luna**. GPT-5 mini is also deprecated and was rejected. GPT-6 Luna is documented as current, with Responses and structured-output support and no shutdown announced in the retrieved deprecation list. Account-specific access cannot be established until the credential is configured. [Official excerpts](official-source-excerpts.md) and [verification record](model-verification.json).

## Exact proposed paid request

- **Model:** `gpt-6-luna`; Standard service tier; reasoning `none`; JSON-object output; `store=false`; no tools.
- **Evidence:** existing Kaspi cutoff **25 October 2026, 20:07:26 GMT**. This is a compact selection of existing evidence, not a fresh company-retrieval run. [Exact evidence](pilot/evidence.json), [request](pilot/request.json), [manifest and hashes](pilot/manifest.json).
- **Size:** 33,559 evidence bytes, reduced from 210,414. Four annual observations and three deterministic calculations retain exact numerical binding; 14 citations preserve source text, URLs, dates, periods and provenance. Two current official-news/disclosure records retain metadata and resolve actual content to the citation register. Key findings, annual/interim distinctions, financial-group warnings and missing independent-news/table coverage remain. Unsupported table records and discovery-only headlines are excluded from claim support.
- **Verified rates:** $0.10/M ordinary input, $0.01/M cached input, $0.125/M default cache-write input, $0.50/M output. The reservation uses the highest applicable default input rate, not a cache-discount assumption. Cache writes replace ordinary input billing; no 12-hour caching, Fast tier or long-context premium is requested.
- **Conservative charge allowance:** 35,644 input tokens using the UTF-8 byte bound, plus at most 2,400 output tokens: **$0.0056555**. This is a conservative estimate, not a measured tokenizer count or provider billing guarantee.
- **Fixed application cap:** **$0.01 total, exactly one request, no automatic retries**. The shared ledger retains the reservation after timeout, HTTP error, incomplete response or validation failure. Do not reset the ledger or issue a substitute request after failure.

**Required setup:** enter `FINSIGHT_OPENAI_API_KEY` through the secure environment binding and ensure it is available to this runtime. No further network broadening is indicated by these checks. Then perform a no-cost authenticated model-availability check. Explicit authorization of the displayed one-request cap is still required before generation.

## Execution and review boundary

The next paid operation must use the existing application's `OpenAIProvider`, the exact prepared compact evidence and the recorded configuration. Verify the reconstructed request hash before sending; preserve the provider response, usage and measured latency. Validate citations and numerical records with the existing application checks, then manually apply the [four-part rubric](../2026-10-25-mvp/pilot/evaluation.md): prioritisation, factual support, period/scope consistency and unsupported causation. Source existence and exact quotes alone do not establish semantic entailment.

Download verification must inspect a bundle containing the real provider output, exact supplied compact input, source evidence and citation register. Label it application-generated. If generation fails, preserve that failed attempt and its reservation; do not replace it with an assistant-written answer or retry automatically.

**Checks:** 221 tests pass; Ruff lint/formatting and dependency consistency pass. New targeted checks verify compact/full evidence parity, unchanged numerical records and warnings, exclusion of tables, and explicit Standard/no-reasoning configuration. Existing period, currency, unrelated-citation, financial-group, approval and one-request tests still pass.

Actual generation calls **0**, paid spend **$0**, provider inference latency/usage/output **not available**, model-quality score **not assigned**. This preflight does not complete the requested live-synthesis acceptance. No merge, deployment, valuation or company expansion.
