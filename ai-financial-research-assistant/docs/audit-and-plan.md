# Phase 0: repository audit and delivery plan

Audit performed 17 October 2026 against portfolio commit `53287b8` on Linux/Python 3.12.14. Development branch: `feat/finsight-research-mvp`.

## What exists and what is reusable

| Existing project | Inspection and reuse decision | Limits |
|---|---|---|
| Learning notebook + learning log | Preserve both. Reuse the revenue-growth, margin and percentage-point definitions; implement finite-input and period checks in a separate package. | Fictional teaching data; notebook functions do not validate provenance or units. Exercises remain unchecked. |
| Unilever | Read `verify_model.py`, valuation tests, README and validation report. Reuse independent expected-result and sensitivity-test patterns. | 98 saved formula comparisons establish arithmetic, not source correctness. Peer inputs, equity bridge and residual-income assumptions require further work. No DCF copied into Phase 1. |
| KSPI | Read `analyse.py`, tests and validation report. Reuse strict schemas, explicit assumptions, undefined-ratio handling and deterministic functions. | Dividend/FX/capital assumptions are scenario-specific. A financial institution model is outside this operating-company MVP. Cached Excel results are not native Excel recalculation. |
| Consumer lending | Read calculation, loader and tests plus credit committee note. Reuse chronological separation, duplicate detection and legitimate-loss handling. | All borrower data are synthetic; lending economics are not corporate reporting metrics. No customer records imported. |

Earlier environment onboarding passed 63 existing portfolio tests and the workbook checks. Those results do not establish that the models are suitable for new companies. This milestone adds its own tests and does not import sibling `analyse.py` modules, whose repeated names would otherwise collide.

## Architecture

`app/main.py` → `finsight.sec` / `csv_import` → validated `models` and `selection` → pure `financials` → `exports`.

Pydantic validates boundaries. `Decimal` retains source precision. pandas is used for display, not financial arithmetic. Streamlit provides a local interface without a frontend build system. requests provides bounded HTTP operations. openpyxl writes spreadsheet exports. No database, LLM, document parser, vector store or agent framework is needed.

Python 3.12 is the reproducible environment target. The app has its own virtual environment because the portfolio numerical studies have a different pinned dependency set. The original notebook and other projects remain intact. No licence is added.

## SEC feasibility and current blocker

Attempted the official API documentation page, CompanyFacts endpoint and identified live requests. This cloud proxy returned HTTP 403 / CONNECT denial before CompanyFacts could be retrieved. Consequently **current official documentation, fair-access policy and redistribution terms could not be verified from this runtime**, and no real-company reconciliation is complete. Links to verify before public deployment:

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/os/accessing-edgar-data
- https://www.sec.gov/about/privacy-information
- https://www.sec.gov/files/company_tickers.json
- https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
- https://data.sec.gov/submissions/CIK0000320193.json

The connector uses the documented SEC endpoint shapes, a configurable identifying User-Agent, at most one request per second per process (including retries), a 24-hour cache and no third-party mirrors. The 1 req/s choice is deliberately conservative; it is not a claim that the current SEC limit was verified. Multi-process deployments must coordinate aggregate limits before deployment.

`www.sec.gov`, `data.sec.gov` and `api.github.com` were added to the cloud configuration draft. Saving that draft does not apply it to the running network policy. No raw real-company dataset is redistributed. Fixture values are explicitly fictional and have no real filing links. Git HTTPS read access worked; the GitHub API was denied by the network proxy.

## Acceptance and manageable milestones

1. **Data core:** strict typed observations, explicit annual selection, manual import, arithmetic, retained competing values, exact exports and independent unit/integration tests.
2. **Usable workflow:** Streamlit company selection, loading/error states, financials, ratios, source review, CSV preview and downloads. Exercise the interface in a real browser as well as AppTest.
3. **Evidence/review:** pinned environment, scoped CI, walkthrough, uncompleted learning exercises, validation evidence, feature-branch commits and PR if access permits.

Phase 1 is **not complete** until Apple and Microsoft each have at least three annual periods retrieved, selected figures reconciled to official disclosures and the real-company user workflow checked. Offline tests validate engineering behaviour, not authentic financial inputs.

## Remaining backlog, in order

- Apply the saved network additions and retry official documentation and live data.
- Run `scripts/validate_live.py`; investigate any schema/selection differences without relaxing financial controls merely to pass.
- Independently reconcile selected revenue, operating income, CFO and PP&E purchases for three periods per company; populate `docs/reconciliation.csv` with actual evidence and discrepancies.
- Complete the live company UI walkthrough and resolve any material issues.
- Publish the feature branch and create a review PR if GitHub access allows; never merge automatically.
- Gather user feedback after the verified MVP. Phase 2 concept enrichment, Phase 3 documents, Phase 4 AI, Phase 5 valuation and deployment remain separate future work.

No financial assumption needs a user decision for this scope. SEC identification is local runtime configuration, supplied separately from code. No paid services are introduced.
