# Company research validation — 20 October 2026

The local application starts and the deterministic name-to-report workflow passes offline tests and browser replay. **Fresh source retrieval in the current cloud instance is blocked by its proxy policy.** The saved configuration lists SEC/news/IR domains, but the runtime reports only package-manager destinations. Saving a draft, publication and a running instance's effective network policy are separate facts. Review/save the required domains in environment settings and publish, then rerun live validation; do not mark this complete until it succeeds.

## Current checks

- Python 3.12.14: **133 pytest tests passed**, Ruff lint/format passed and `pip check` found no broken requirements. Tests include Streamlit AppTest for ambiguity, coverage failures and export availability.
- Production Streamlit service started successfully. Chromium exercised the fictional example, hand-checked ratios, CSV/XLSX downloads, invalid/valid uploads, source review, mode reset and missing-SEC-configuration error.
- Chromium historical replay exercised Apple, Microsoft, Kaspi.kz and NVIDIA through the name form, report and downloaded ZIP. ZIP contents included citations and a financial workbook only for supported profiles. Explicit Apple confirmation, no-match messaging and old-report clearing passed. KSPI's report retained the warning that CFO is not distributable cash. Replay has visible test labels and preserved 18 October cutoffs; it is not fresh source validation.
- A fresh `scripts/validate_research.py --refresh` run at **2026-10-20 17:37 UTC** exited **1**. All four name searches and both ambiguity/no-match probes recorded SEC connection failure after bounded retries. No replacement data was substituted. Direct source probes also returned proxy connection errors. The OpenAI status site could not be reached from this instance, so it does not establish the cause of the earlier environment outage.
- Environment status reported running/connected with current observations. That establishes startup, not source access or a successful future snapshot restoration.
- No model API key, opt-in flag or model ID was configured. **Actual model requests: 0. Actual model spend from this work: $0.** Mocked provider tests cover reservations, failed-call budget retention, returned usage and malformed/citation/numeric-output rejection.

## Historical real-source evidence

The live name-based validation on **18 October 2026** retrieved official filings, linked earnings exhibits and RSS metadata. A subsequent same-day cached rerun added IR discovery and the 12-story independent-news budget:

| Query / selected ticker | Initial end-to-end seconds | Cached rerun seconds | Documents registered / read | News records retained | Citation IDs | Financial extraction |
|---|---:|---:|---:|---:|---:|---|
| Apple / AAPL | 19.48 | 0.83 | 16 / 15 | 13 | 62 | Supported |
| Microsoft / MSFT | 8.13 | 1.04 | 6 / 5 | 14 | 66 | Supported |
| Kaspi.kz / KSPI | 35.90 | 1.54 | 21 / 20 | 16 | 57 | Supported |
| NVIDIA / NVDA | 16.91 | 0.60 | 15 / 15 | 13 | 22 | Explicitly unsupported |

Timing includes search/report/export, depends on cache/network, and is not a performance guarantee. The initial run had a wider news budget, so its outputs differ from the cached rerun. Independent news retained here was headline metadata, not read articles. Each supported issuer had one unread IR landing page and incomplete presentation discovery; no full presentation coverage was claimed. The updated financial-event search query is regression-tested but **has not yet been live-validated** under the current blocked policy.

Apple matched three listings and the validator explicitly chose CIK 0000320193. “American” returned multiple candidates; “NonexistentPrivateExampleZZZ” returned none. NVIDIA demonstrated company identification/document retrieval without silently substituting another company's financials. Latest annual periods in these snapshots were Apple 2025-09-27, Microsoft 2026-06-30 and KSPI 2025-12-31. News window: 2026-07-21 through 2026-10-18; cutoff approximately 20:51 UTC. These dates remain visible during replay.

The earlier [48-value independent reconciliation](validation.md) remains distinct from document extraction: quoted source text or a hash does not verify all accounting. Figures and calculations preserve review warnings; the system does not label every source or report verified. Numerical/metadata contradictions are flagged, but exhaustive semantic contradictions across filings/news are not automatically established.

## Optional model estimate, not provider pricing

At **illustrative assumed rates** of $1/million input tokens and $2/million output tokens, the same historical evidence gives these conservative byte-based input allowances, each with a 1,200 output-token maximum:

| Company | Input allowance | Estimated reservation |
|---|---:|---:|
| AAPL | 67,959 | $0.070359 |
| MSFT | 73,120 | $0.075520 |
| KSPI | 64,436 | $0.066836 |
| NVDA | 13,177 | $0.015577 |

These are not measured tokenizer counts, current vendor prices, or charges. Current report content and configured prices determine the estimate displayed before approval. No optional-model quality or real-provider integration claim is made from mocked tests. See [setup and budget behavior](research-guide.md).

## Reproduce

From `ai-financial-research-assistant`, use the project's environment:

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pip check
# With real SEC_USER_AGENT and source network access:
.venv/bin/python scripts/validate_research.py --refresh --output exports/research-validation
# Normal app:
bash scripts/start.sh
```

For an optional browser replay, `scripts/replay_research_app.py` requires externally saved `AAPL-evidence.json`, `MSFT-evidence.json`, `KSPI-evidence.json` and `NVDA-evidence.json` from the validator. Full filings/evidence are not bundled in Git. Set `FINSIGHT_REPLAY_DIR` to that directory and launch it with Streamlit on port 8507. Run `scripts/browser_research_smoke.py` with a Python that has Playwright and Chromium; set `FINSIGHT_CHROMIUM` if the executable is elsewhere. This harness replaces provider functions only in the test app, and never affects the production launch path.

Local evidence retained for this session: `/workspace/finance-validation/research-v1/`, `/workspace/finance-validation/research-v1-final/` and `/workspace/finance-validation/research-2026-10-20/`. The screenshot is `/tmp/finsight-research-kspi.png`. These paths are not a promise of delivery through Git or restoration into another machine. Native Intel Mac, desktop Excel, fresh live access after policy application and real optional model generation remain unverified. No merge or deployment was performed.
