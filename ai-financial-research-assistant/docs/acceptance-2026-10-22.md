# Focused acceptance — 22 October 2026

**Historical record:** the [23 October follow-up](news-review-2026-10-23.md) supersedes the Guardian network blocker, Microsoft redirect and test counts below.

Continues `8f47a0f`, preserving `50c7ca1` and the existing annual accounting, KSPI, CSV, Excel and model-spending safeguards. **Fresh official-source research and the production-app journey work. Acceptance remains incomplete because no independent original article has yet been retrieved live.** No merge, deployment or paid model call occurred.

## Published environment and fresh requests

The running executor now lists the seven previously configured custom hosts. Runtime observations are current, but the status API reports policy state `unknown`, so configuration alone is not treated as proof of enforcement. Actual requests through the inherited proxy/TLS path returned HTTP 200 from SEC submissions, Google RSS and the authenticated GitHub PR API. This resolves the previous SEC/GitHub CONNECT blocker. See [runtime observations](evidence/acceptance-runtime-2026-10-22.json) and [timestamped source probes](evidence/acceptance-source-probes-2026-10-22.json).

The uncached company-name validator bypassed the directory, submissions, documents, RSS and CompanyFacts caches. These are fresh requests, not historical replay. It exited **1 because all three outcomes are partial**, not because report generation failed. The [full fresh register](evidence/acceptance-fresh-2026-10-22.json) records each attempt, retrieval time, URL, hash, cache flag, document outcome, selected disclosure, news metadata and coverage.

| Company | Fresh run UTC | Registered documents read | Financial observations | News items / selected contents read | Outcome |
|---|---|---:|---:|---:|---|
| Apple | 21:06:26–21:06:51 | 16/16 | 40 | 13 / 1 | Partial: independent article text unavailable |
| Microsoft | 21:06:51–21:07:05 | 5/6 | 40 | 14 / 2 | Partial: independent article text unavailable; IR landing page unread |
| Kaspi.kz | 21:07:05–21:07:37 | 21/21 | 27 | 16 / 3 | Partial: independent article text unavailable |

Document counts include the IR discovery page; substantive-document counts in `coverage.json` exclude it. Selected news contents above are **official disclosures**, not independent articles. Independent articles read: **0 for all three**. Microsoft's reviewed IR URL returns HTTP 301; automatic redirects remain disabled. SEC documents and financial evidence still survive that gap.

An earlier uncached baseline run at 21:01–21:02 also reached all three companies. Its old outcome logic marked Apple/KSPI complete despite missing independent article text. The final assessment now requires a read original article on the reviewed independent publisher route and exposes the missing coverage. That baseline is not substituted for the final results above.

## Latest-document correction

`research/evidence.py` parses strict ISO calendar dates before ranking. A dated SEC release cannot lose to `Not established`, an empty date, an impossible date or arbitrary text. Such publication dates are excluded from latest ranking; relevant undated documents remain separately labelled supplementary evidence with explicit warnings in the report and optional model package. Invalid report-period dates cannot sort ahead of valid periods; their missing context remains explicit. Supplementary evidence cannot satisfy the latest-disclosure coverage check by itself.

The fresh selections are Apple's 31 July 10-Q (period ended 27 June) and 30 July earnings release; Microsoft's 29 July earnings release; and Kaspi.kz's 12 August interim exhibit and 10 August earnings release. MSFT has no later 10-Q in the bounded annual-baseline selection; the release is not labelled an interim filing. SEC current-report dates remain metadata, not an inferred financial period end.

## Narrow independent-news route and remaining action

The free public Guardian route discovers direct article URLs from reviewed Apple/Microsoft technology feeds or the banking feed for Kaspi.kz. It filters company/event headlines and the requested publication window, retains at most three discoveries, and reads at most **one** independent article within the existing three-source content budget. The banking feed may have no Kaspi.kz coverage; it is not an archive/search service. Zero matches cannot establish no news.

Only exact HTTPS `www.theguardian.com` feed paths and dated `/technology/YYYY/mon/DD/slug` or `/business/...` article paths are admitted. Userinfo, ports, query redirects, fragments, malformed dates, other hosts and liveblog paths are rejected. Redirects remain disabled. Extraction requires a marked public article body; navigation, consent pages and subscription prompts are not substituted for text. No paywall bypass, wrapper decoding, paid provider or new dependency was introduced.

Headline, publisher, publication date, unknown/established event date, original URL, discovery feed/hash/time/cache flag, article hash/time, access state and cited excerpts remain in the evidence bundle and model inputs. Google wrappers stay discovery-only. Matching original/feed headlines can be deduplicated while retaining the alternate URL.

**Live blocker:** the actual Guardian feed request received proxy CONNECT **403 Forbidden** before reaching the publisher. The active seven-host policy omits `www.theguardian.com`. The supported configuration tool confirmed a saved draft adding only that host and preserving all existing domains (`requires_publish: true`). Saving is not application. No readable live Guardian article, working current publisher markup or exhaustive news coverage is claimed; route tests use clearly synthetic feed/HTML fixtures.

**Remaining setup action:** review/save the `www.theguardian.com` addition in environment settings and publish. After reconnecting, inspect the effective runtime policy and retry the feed, then retrieve and inspect a relevant original article using the implemented route. If no relevant article is in the bounded feed/window, report that limitation rather than claiming success or spending on a provider. No payment is required for this public route; any future paid option needs separate cost disclosure and authorization.

## Production-app journey and readable report

Chromium drove the real `app/main.py`, without patched providers or a replay harness, for all three companies. Apple required explicit legal-entity selection. For each company it enabled source refresh, ran research, reviewed the report, opened **Evidence & coverage → Inspect citation register**, downloaded the ZIP, and checked its report, citation register, coverage, model evidence, source snapshot and financial XLSX. Every successful source retrieval recorded by these research runs had `cached=false`; UI directory searches may reuse their dated cache, while the separate validator above verifies uncached directory search. See [browser results](evidence/acceptance-browser-2026-10-22.json).

The browser test initially timed out clicking Streamlit's hidden checkbox input. The final test uses the keyboard-accessible control and verifies it is checked; no application event handler or network call is mocked. All three final journeys passed. Missing independent text is prominent in the outcome banner, report and downloaded coverage; model usage remains zero.

The fresh **Kaspi.kz readable report** combines the FY2025 annual baseline, the three/six-month interim disclosure to 30 June 2026, the 2Q/1H earnings release and subsequent company announcements, with direct SEC citations and clear quarterly/YTD/annual boundaries. Annual financial tables remain normalized annual evidence; recent quoted figures are not annualized or silently mixed into annual calculations. Financial-group cash-flow warnings remain present. The report does not supply independent news conclusions from Google headlines.

Local review artifacts:

- `/workspace/finance-validation/acceptance-final-2026-10-22/{AAPL,MSFT,KSPI}-report.md`, `*-research.zip`, `*-evidence.json`.
- `/workspace/finance-validation/acceptance-browser-2026-10-22/`: downloaded bundles, screenshots and timestamped browser outcomes.

Full source text is retained locally in the evidence artifacts, not redistributed through the Git review register. The older KSPI demonstration is explicitly historical and is not this fresh acceptance result.

## Checks and limits

**178 tests passed** on Python 3.12.14. Ruff lint and formatting pass; `pip check` reports no broken requirements. The prior 156 tests remain, with regressions for date ordering/invalid dates, supplementary report/model evidence, source allowlist rejection, redirects, body-only extraction, consent-page rejection and provenance-preserving discovery-to-original retrieval. Existing wrong-metric/year/currency/source/citation numerical-claim tests remain passing. Browser acceptance passed for **3/3 production journeys**.

The authenticated PR description is updated to the current functionality, checks and unresolved article-access limitation. Paid model calls: **0**, cost **$0**; generation remains disabled. No merge or deploy. Native macOS/desktop Excel acceptance, actual model-provider billing, semantic claim verification, complete presentation discovery and live independent article extraction remain unverified or incomplete.
