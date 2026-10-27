# One Gemini free-tier candidate — verification blocked

**Do not select or integrate a Gemini model on the strength of this note yet.** Fresh public-documentation GETs on 26 October 2026 to `ai.google.dev` all received proxy CONNECT 403. No model API endpoint was called, no credential was requested, and no workaround was used. [Actual access record](gemini-documentation-access.json).

The one provisional candidate to investigate is **Gemini 2.5 Flash-Lite through the Gemini Developer API**. Its historically available free tier makes it a plausible low-cost structured-synthesis candidate; that is background knowledge, **not a verified claim about current availability, free allowance or lifecycle**. The exact maintained replacement, if this model has since retired, must come from the official model/deprecation pages rather than an invented model ID. No current recommendation or numeric quota is asserted.

| Decision item | Current evidence and required check |
|---|---|
| Eligibility | Unverified. Check [available regions](https://ai.google.dev/gemini-api/docs/available-regions) and official terms for account, age, location, project and data-use eligibility. This task did not inspect the user's country or Google project. |
| Model availability/lifecycle | Unverified. Check [models](https://ai.google.dev/gemini-api/docs/models) and [deprecations](https://ai.google.dev/gemini-api/docs/deprecations) before choosing an ID. A model documentation listing would still not prove access for the user's account. |
| Free-tier pricing | Unverified. Check the exact model's [pricing row](https://ai.google.dev/gemini-api/docs/pricing), including input/output and any excluded features. A ChatGPT/Gemini consumer subscription is not evidence of Developer API quota. No billing enablement is proposed. |
| Quotas | Current RPM, input/output token limits, requests/day, reset timing and available project quota are unverified. Check [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and the project's displayed limits; do not reuse remembered numbers. A free allowance is not a capacity guarantee. |
| Structured output and request size | Confirm current JSON output support and whether this compact evidence plus output allowance fits the chosen model/context and project token quota. The existing output validator must remain authoritative. |
| Data terms | Verify treatment of free-tier prompts/outputs and suitability for the evidence. Do not add private financial information on an assumption that free-tier data handling matches paid services. |

## Smallest integration change, if confirmed and later authorised

Keep `OpenAIProvider`, its existing defaults and ledger intact. Add only one Gemini adapter implementing the existing `NarrativeProvider.generate(evidence, approved=...)` interface. Send the same compact JSON evidence and synthesis instructions; map provider JSON text and usage to the existing `validate_narrative` result and audit shape. Reuse exact numerical binding, eligible citation checks, the one-request ledger and failure preservation. Use one fixed reviewed endpoint/model, no tools, no automatic retries or paid fallback. Keep the actual request's supplied evidence with its download.

There is one concrete spending-policy issue to address: current `ModelConfig.from_environment()` requires positive prices, and budget reservation is implemented inside the OpenAI adapter. Do not bypass those checks by pretending paid prices are zero. A confirmed free-only route needs an explicit eligibility/billing-disabled gate and a shared request counter independent of dollar spend, with targeted tests. The application cannot make a provider account free merely by setting a local dollar cap. No such adapter or gate was built in this task.

Estimated implementation/evaluation effort after documentation access, free-tier eligibility and a key are settled: **2–4 hours**, assuming the maintained model supports JSON output, no SDK dependency is required, and one permitted request fits the free quota. Provider quality, quota behaviour and latency remain untested. This is not a commitment to use Gemini.

**Next prerequisite for this decision:** permit access to the public documentation host `ai.google.dev` through supported environment settings. Do not broaden network access to model API hosts merely to read documentation. The runtime metadata is known to lag effective configuration, so do not replace an uncertain allowlist or infer success from saving it; retry the actual documentation request after the change. Meanwhile, the no-API report/manual-export workflow remains usable.
