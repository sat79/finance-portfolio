# Independent review follow-up — 21 October 2026

The current company-research milestone now has evidence-based outcomes, recent disclosure analysis, a bounded news-content step and an auditable model payload. **Fresh end-to-end operation remains blocked by the environment proxy.** The prior work at `50c7ca1` and the annual financial/KSPI safeguards are retained. This follow-up does not expand financial coverage or enable paid calls.

## Fresh source access: actual result

Runtime status reported `running`, `connected`, current observations and an enforced restricted network policy with **no custom allowed hosts**. The executor's `/etc/codex/network-policy.json` agrees: only package-manager/bootstrap destinations are present. The saved environment configuration contains `www.sec.gov`, `data.sec.gov`, `news.google.com`, `investor.apple.com`, `www.microsoft.com`, `ir.kaspi.kz` and `api.github.com`. That saved policy is not reflected in the running instance.

A proxy `CONNECT` request returned **HTTP 403 Forbidden** for SEC and GitHub API before establishing an origin connection. This is an environment egress denial, not evidence of an SEC contact-address rejection, an expired GitHub credential, a paid-news limitation or an application parsing error. Proxy and TLS settings were preserved; no alternate route or restriction bypass was attempted.

`validate_research.py --refresh --companies Apple Microsoft Kaspi.kz` now bypasses **all** caches, including the company directory. It exited **1**. The [recorded fresh outcomes](evidence/review-fresh-2026-10-21.json) contain attempted/finished timestamps, URL, cache policy, actual failure and explicit unattempted downstream coverage:

| Name | Fresh attempt (UTC, 21 October) | Outcome | Extracted documents | News and financial coverage |
|---|---|---|---:|---|
| Apple | 01:06:48–01:06:51 | Failed at official directory request | 0 | Not attempted: company resolution failed |
| Microsoft | 01:06:51–01:06:55 | Failed at official directory request | 0 | Not attempted: company resolution failed |
| Kaspi.kz | 01:06:55–01:06:59 | Failed at official directory request | 0 | Not attempted: company resolution failed |

There is no retrieval timestamp, hash or source-content success to claim for these failures. No cached identity, financial profile or fictional data was substituted. Separate historical replay is described below.

**Remaining setup action:** review/save the resaved seven-domain configuration in environment settings, then publish the environment. After reconnecting, check `environment_status` for the custom domains with `state=enforced`, and retry the actual requests. If the saved/published domains still do not appear, this needs platform configuration-to-runtime synchronisation support; repeating draft saves or reinstalling Python will not fix the denial. Saved configuration and publication alone are not successful source-access tests. `api.github.com` is also required to update the PR description through the existing authenticated proxy.

## Outcome and evidence changes

- **Failed:** neither substantive readable source documents nor selected financial observations exist. A name match, RSS metadata or rendered template cannot turn this into success.
- **Partial:** useful evidence survives, but identity/stage failures, missing annual/recent text, unread registered documents, unsupported financial extraction or missing selected news content leave gaps.
- **Complete:** the bounded evidence checks and stages pass. This explicitly does not mean exhaustive discovery, all sources independently verified, or a semantically verified conclusion.

The UI, Markdown, ZIP `coverage.json` and validator use the same assessment. Partial/failed runs do not display successful completion; retained evidence and diagnostics remain exportable.

The latest registered 10-Q and recognised foreign-issuer interim exhibit contribute period headings and relevant passages. Earnings selection prefers the actual release over its same-day filing cover. Quarterly/three-month, six/nine-month or half-year/YTD and annual cues are shown with exact source locations. A current-report date is not silently treated as a financial period end. Interim figures remain unnormalised quoted evidence; the reviewed calculation table remains annual-only. No quarter-to-year arithmetic, annualisation or recycled annual cause is introduced.

Up to three relevant news/announcement sources contribute selected text. Already retrieved official SEC announcements are reused with their original hashes/timestamps; directly accessible permitted original URLs use the bounded transport. Google RSS wrappers remain discovery-only; no wrapper decoding, arbitrary redirects or paywall circumvention occurs. Access interstitials are not treated as read articles. A narrow extractor establishes past meeting/resolution event dates only when an explicit quoted source supports the date; other event dates remain unknown. Metadata-only items produce no substantive conclusion. The source allowlist is still narrow, so independent article coverage remains incomplete.

## Optional model payload and claim checks

The actual payload is downloadable as `model-evidence.json` even while generation is disabled. It contains identity and provenance, cutoff, news window, full structured news metadata/access records, selected news contents, annual and recent cited excerpts, selected financial observations, deterministic calculations and warnings, plus coverage gaps. Citation IDs refer to the supplied text/records; a URL by itself is not accepted as support for model prose.

Numerical output uses structured records copied from `quantitative_evidence`. Every field must match the cited record: metric, exact value, period start/end, currency, unit, source URL(s) and citation ID(s). The application renders these tuples itself; arbitrary numerical prose is rejected. Calculations carry their deterministic formula/input records and warnings in the payload. Tests reject the correct number attached to a different metric/year/currency, an unrelated existing citation, altered source URLs and invented values.

Management explanations must be verbatim supplied disclosure excerpts. Interpretations require exact supporting excerpts tied to each citation and remain explicitly **unverified**. These checks establish structural/source binding, not semantic relevance, truth, causal entailment or comprehensive detection of numerical assertions expressed in words. A fluent interpretation can still be wrong; no automated semantic verification is claimed. The model cannot add normalized quarterly figures by paraphrasing a table. Human review remains necessary.

Paid generation is still opt-in and disabled. Existing estimates, explicit approval, bounded output, locked cumulative reservation ledger and failed-request reservation retention remain. **Actual paid model calls in this work: 0; spend: $0.** Provider tests use mocks, not a live billing/API integration.

## Validation and demonstration

- **156 tests passed** on Python 3.12; Ruff lint/format and dependency consistency checks passed. Existing annual selection, Excel precision, CSV validation and KSPI safeguards remain covered.
- Targeted regressions cover all-retrieval failure, partial preservation, unread documents, failed UI state, recent-period context, release-versus-cover selection, foreign interim recognition, date evidence, original-source reads/interstitials, complete model content, wrong numerical bindings and unrelated citations.
- Chromium exercised historical name-to-report replay for AAPL, MSFT, KSPI and NVDA, including partial outcomes, report/citation/model-evidence downloads, explicit ambiguity selection and unsupported-search clearing. The production app's synthetic/CSV/Excel browser checks passed separately.
- The [KSPI reading demonstration](kspi-review-demonstration.md) combines annual 2025 context, the interim disclosure for the three/six months ended 30 June 2026, the 2Q/1H earnings release and a subsequent shareholder-resolution announcement. It is an excerpt of a newly rendered **historical** report, retaining 18 October provenance. Its outcome is partial, including inaccessible IR/presentation coverage. The companion AAPL replay combines FY2025, the June 2026 10-Q and earnings release. Neither is fresh validation.

Full local artifacts: `/workspace/finance-validation/review-demo-2026-10-21/{KSPI,AAPL}/` contains `report.md`, `research.zip`, `model-evidence.json` and `coverage.json`. They are not full-source datasets redistributed through Git. Reproduce the rendering with:

```bash
.venv/bin/python scripts/render_research_snapshot.py \
  --input /path/to/KSPI-evidence.json --output exports/review-demo/KSPI
```

No new financial-company mappings, valuation, deployment or merge were added. Native Mac/desktop Excel acceptance and actual optional-provider generation remain unverified. The PR description API update was attempted at 01:17:15 UTC on 21 October and failed with the same proxy CONNECT 403. The remote PR description therefore remains stale. Its replacement title is “FinSight: cited company research with evidence-based outcomes and claim controls”; the prepared body is [here](pr-description.md). Apply it once api.github.com access is enforced; no remote update is claimed.
