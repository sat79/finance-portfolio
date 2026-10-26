# Official sources checked on 26 October 2026

Retrieved pages returned HTTP 200; source hashes and URLs are in model-verification.json. These are short verbatim excerpts, not full-page copies.

- [Deprecations](https://developers.openai.com/api/docs/deprecations): “On October 14, 2026, we notified developers using certain GPT-4 series models of their deprecation and removal from the API on January 14, 2027.” The table pairs GPT-4.1 mini with recommended replacement `gpt-6-luna`. The same page also lists GPT-5 mini for shutdown on 11 December 2026; it was rejected as an alternative.
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna): “Our most efficient model for focused, high-volume tasks.” “reasoning.effort supports none, low, medium (default), high, xhigh, and max.” The page lists Responses and structured-output support, a 1,050,000-token context window and 128,000 maximum output tokens. No deprecated label or scheduled shutdown was found for this model.
- [Pricing](https://developers.openai.com/api/docs/pricing), Standard table: `gpt-6-luna` — input $0.10, output $0.50, cached input $0.01, 30m cache write $0.125, 12h cache write $0.25, all per million tokens.
- [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): “Cache-write pricing is not an additive fee: input tokens use the uncached-input, cached-input, or cache-write rate.” “For GPT-5.6 and later, cache writes cost 1.25× the standard, uncached input-token rate for the default 30-minute lifetime.”

Documentation establishes public model compatibility and advertised rates, not this account's access. The unauthenticated model-list request returned HTTP 401. No secret value was read or exposed; neither supported application credential variable was present. Runtime metadata still reports revision 6 and the old allowlist even though fresh requests prove network access now works.
