# Live news and Kaspi report review — 23 October 2026

Continues `9ea6ad5` on PR #1. The narrow live-news acceptance now succeeds, the Microsoft canonical IR endpoint works, and a complete fresh Kaspi report/evidence bundle is available with a separate analytical critique. **Kaspi remains partial because the bounded independent feed has no matching article.** That does not imply no news exists. Financial extraction remains limited to **AAPL, MSFT and KSPI**. No paid model calls, merge or deployment.

## Real source requests

The runtime status and startup policy still omitted Guardian and reported enforcement state `unknown` when inspected. Actual uncached requests through the inherited proxy returned HTTP 200 for the Guardian feed and original articles. Therefore the prior network blocker is resolved operationally; the stale metadata is not described as confirmed enforcement. No proxy, TLS, URL safeguards or paywall controls were bypassed, and no further domain change was requested. [Initial timestamped probes](evidence/news-source-probes-2026-10-22.json) and [fresh three-company source register](evidence/news-review-fresh-2026-10-23.json) preserve the evidence.

The first original Apple article body extracted successfully but the passage selector missed its CEO/leadership content. That concrete mismatch with the discovery terms is fixed and regression-tested. This initial outcome was **body extracted, no relevant excerpt selected**, not a network failure or a successful cited-article result. The final fresh runs supply actual excerpts and citations:

| Company | Original article | Published UTC | Retrieved UTC, 23 October | Exact body citations |
|---|---|---|---|---|
| Apple | [CEO at annual showcase](https://www.theguardian.com/technology/2026/sep/09/apple-product-showcase-ceo-john-ternus) | 9 September, 19:07:53 | 02:12:17.422089 | `NDocN7febf8d308:B1`, `:B8` |
| Microsoft | [AI regulation and safety](https://www.theguardian.com/technology/2026/oct/12/ai-less-regulated-than-milk-microsoft-president-calls-for-tougher-rules) | 12 October, 07:52:46 | 02:12:36.879566 | `NDocN9348a6c236:B1`, `:B4` |

The [live article records](evidence/news-live-2026-10-23.json) include the title, publisher, URL, publication date, retrieval time, body excerpts, source locators, feed provenance and article hashes. Both RSS publication timestamps agree with `datePublished` in the corresponding original HTML; `dateModified` was not substituted. Event dates remain unestablished. Original article text was inspected, not merely headlines. The Apple story supports a leadership-development record; the Microsoft story supports attributed reporting about regulation. Neither establishes financial impacts or verifies the speakers' interpretations.

The route still reads at most one independent original per company, from the reviewed public publisher, within the existing three-source news-content budget. The other Apple discoveries remain clearly labelled budget-exhausted/discovery-only. No paid provider was used.

Microsoft's old `/en-us/Investor` URL returned HTTP 301 with `Location: https://www.microsoft.com/en-us/investor/default`. A separate direct HTTPS request to that same approved host returned 200 and readable HTML. The reviewed landing URL now uses that canonical endpoint. Automatic redirects remain disabled; bounded linked-document retrieval remains at two. The fresh Microsoft run reads 8/8 official registered documents, including the landing page and two linked records. Undated IR records retain supplementary labels rather than displacing dated SEC evidence.

## Fresh coverage and app validation

All timestamps below are UTC; the run occurred at 03:11–03:13 BST on 23 October. Every successful source request in the validator has `cached=false`, including company-name resolution.

| Company | Fresh run UTC | Official documents | Financial extraction | Independent news | Bounded outcome |
|---|---|---|---|---|---|
| Apple | 02:11:51–02:12:21 | 16/16 read | 40 annual observations | 1 original read from 3 direct discoveries | Complete bounded checks |
| Microsoft | 02:12:21–02:12:40 | 8/8 read | 40 annual observations | 1 original read from 1 direct discovery | Complete bounded checks |
| Kaspi.kz | 02:12:40–02:13:12 | 21/21 read | 27 annual observations | Feed fetched, 0 matching direct discoveries | Partial |

Official counts include IR discovery pages; substantive counts exclude those pages. “Complete” explicitly does not mean exhaustive coverage or verified claims. The validator exits 1 because Kaspi remains partial. Its Google RSS headlines are not substituted for independent text. The successful Guardian banking feed's lack of a matching Kaspi article is distinct from a failed request, malformed discovery feed, inaccessible article, failed body extraction or extracted body with no relevant selected passage. Those states now have separate machine statuses and readable report/UI labels.

**185 tests pass**, including seven new cases for the actual leadership-selection defect, network-failure classification and separated coverage outcomes. A report-level regression also fixes an impossible publication date crashing the stale-disclosure check; the existing supplementary-date label is retained. All prior financial, date/citation and spending safeguards remain passing. Ruff lint/formatting and dependency checks pass. **Three production-browser journeys passed** against `app/main.py`: name, confirmation, refreshed sources, report, citation inspection, downloaded ZIP and workbook. The [browser register](evidence/news-browser-2026-10-23.json) records actual outcomes. Final friendly coverage labels are additionally checked by report regressions. Browser and validator runs are fresh and separate; neither uses the replay harness.

## Complete Kaspi review artifacts and analytical usefulness

Local deliverables under `/workspace/finance-validation/kspi-review-2026-10-23/`:

- `KSPI-full-report.md`: complete generated report, not a selected excerpt.
- `KSPI-evidence.zip`: original eight-file application bundle, including full normalized research evidence, citations, coverage, model evidence, registers and financial XLSX.
- `KSPI-analytical-review.md`: separate analyst critique with reported facts, exact calculations and unverified interpretations clearly distinguished.
- `KSPI-review-package.zip`: all original bundle entries plus the critique, its 26-entry source register, calculation ledger, and disabled pilot specification/evidence.
- `review-manifest.json`: sizes, SHA-256 hashes and original research cutoff. ZIP CRCs and exact passage/locator matches were checked.

The [readable critique](kspi-analytical-review-2026-10-23.md) identifies the central revenue/profit conversion question, separates annual changes from quarterly and balance-sheet evidence, and traces e-Commerce, funding costs, payments mix, Stage 3 restructured loans and dividend approval to exact retrieved source blocks. [Review citations](evidence/kspi-review-citations-2026-10-23.json) and [Decimal calculations](evidence/kspi-review-calculations-2026-10-23.json) distinguish extra analyst-selected evidence from the automated report's narrower selection.

The critique's conclusion is candid: the generated report is useful as an auditable evidence pack, but repetitive warnings and heuristic passage ranking bury the most material developments. It does not yet provide a quantified comparable-scope profit bridge, prioritized bank-risk analysis or independently corroborated Kaspi developments. It is not a sufficient basis for valuation. No hardcoded company narrative or extra company coverage was added to the application.

## Optional synthesis pilot — prepared, not executed

A single-request pilot uses a selected, provenance-preserving subset of the fresh Kaspi evidence, the existing structured response contract, at most 1,200 output tokens and a conservative **30,766-input-token allowance** (UTF-8 byte bound, not measured tokenization). Its purpose is to test prioritization and usefulness, not calculate new figures or claim semantic verification. Unsupported causal claims, mixed periods or missing source support fail human review; existing numerical/citation checks and locked spending reservations remain mandatory.

[Cost specification](evidence/kspi-synthesis-pilot-2026-10-23.json): at **illustrative, unverified** prices of $1/million input and $4/million output tokens, the reservation is **$0.035566**. This is not current provider pricing or a billing quote. The proposed ceiling is $0.10 for one request, with no automatic retries. A model must be selected, current prices verified, and explicit spending authorization obtained before any call. Actual model calls/spend: **0 / $0**. The pilot remains disabled.

**Single next action:** review the Kaspi analytical memo and its five evidence-backed open questions before deciding whether an automated synthesis pilot is worthwhile. No further network configuration is currently needed for the tested route.
