# Current product direction

The updated [company-name-to-research plan](phase-2-proposal.md) supersedes the original phase ordering below. The implementation adds `finsight.research` for identity, bounded HTML/PDF retrieval, RSS news, deterministic cited reporting and an opt-in narrative provider. Existing financial selection, pure calculations, caches, CSV and XLSX are reused. See [current validation](research-validation.md); the following audit remains historical.

# Phase 0: repository audit and delivery plan

Audit performed 17 October 2026 against portfolio commit `53287b8` on Linux/Python 3.12.14. Development branch: `feat/finsight-research-mvp`.

## What exists and what is reusable

| Existing project | Inspection and reuse decision | Limits |
|---|---|---|
| Learning notebook + learning log | Preserve both. Reuse the revenue-growth, margin and percentage-point definitions; implement finite-input and period checks in a separate package. | Fictional teaching data; notebook functions do not validate provenance or units. Exercises remain unchecked. |
| Unilever | Read `verify_model.py`, valuation tests, README and validation report. Reuse independent expected-result and sensitivity-test patterns. | 98 saved formula comparisons establish arithmetic, not source correctness. Peer inputs, equity bridge and residual-income assumptions require further work. No DCF copied into Phase 1. |
| KSPI | Read `analyse.py`, tests and validation report. Reuse strict schemas, explicit assumptions, undefined-ratio handling and deterministic functions. | Dividend/FX/capital assumptions are scenario-specific. The old bank valuation is not copied; the user-requested KSPI IFRS research profile is developed separately with financial-group controls. Cached Excel results are not native Excel recalculation. |
| Consumer lending | Read calculation, loader and tests plus credit committee note. Reuse chronological separation, duplicate detection and legitimate-loss handling. | All borrower data are synthetic; lending economics are not corporate reporting metrics. No customer records imported. |

Earlier environment onboarding passed 63 existing portfolio tests and the workbook checks. Those results do not establish that the models are suitable for new companies. This milestone adds its own tests and does not import sibling `analyse.py` modules, whose repeated names would otherwise collide.

## Architecture

`app/main.py` → `finsight.sec` / `csv_import` → validated `models` and `selection` → pure `financials` → `exports`.

Pydantic validates boundaries. `Decimal` retains source precision. pandas is used for display, not financial arithmetic. Streamlit provides a local interface without a frontend build system. requests provides bounded HTTP operations. openpyxl writes spreadsheet exports. No database, LLM, document parser, vector store or agent framework is needed.

Python 3.12 is the reproducible environment target. The app has its own virtual environment because the portfolio numerical studies have a different pinned dependency set. The original notebook and other projects remain intact. No licence is added.

## SEC feasibility and access policy

Live retrieval succeeded after the required domain settings became available. The official API, access guidance and privacy/security policy were read on 17 October 2026:

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- https://www.sec.gov/about/privacy-information

The API documentation states that CompanyFacts aggregates non-custom taxonomy observations applying to the entire filing entity, that no API key is needed, and that submissions include at least one year or 1,000 recent filings. Older archives require separate requests and are outside this MVP. The access guidance requests an identifying User-Agent with a contact email; the privacy/security policy sets a maximum of 10 requests/second across machines and may block excessive/unclassified automation. FinSight uses 1 request/second per process, a 24-hour cache and bounded retries. Multiple processes sharing an egress address need aggregate coordination before deployment.

The cloud configuration draft includes `www.sec.gov`, `data.sec.gov` and `api.github.com`. Live requests to these destinations were verified. The project bundles only a small factual reconciliation sample and synthetic fixtures, not whole company filings or full SEC datasets. Access guidance is not a blanket copyright licence for every company-authored document; no such licence is asserted. Public hosting and wider redistribution require a separate review of the then-current terms and content rights.

## Acceptance and manageable milestones

1. **Data core:** strict typed observations, explicit annual selection, manual import, arithmetic, retained competing values, exact exports and independent unit/integration tests.
2. **Usable workflow:** Streamlit company selection, loading/error states, financials, ratios, source review, CSV preview and downloads. Exercise the interface in a real browser as well as AppTest.
3. **Evidence/review:** pinned environment, scoped CI, walkthrough, uncompleted learning exercises, validation evidence, feature-branch commits and PR if access permits.

Acceptance requires live KSPI/Apple/Microsoft retrieval, at least three annual periods, source reconciliation and a user-workflow check in addition to offline tests. See `validation.md` and `reconciliation.csv` for completed evidence; tests do not establish universal financial-data correctness.

## Remaining backlog, in order

- Review this scoped MVP and its reconciliation evidence; merge only after the owner's approval.
- Gather user feedback on source review, missing-data messages and export usability. No time-saving claims have been measured.
- Extend coverage only with company/concept-specific evidence and tests, as Phase 2.
- Keep Phase 3 documents, Phase 4 AI, Phase 5 valuation and deployment as separate future work.

The user explicitly requested all three companies, including KSPI; its IFRS/KZT/20-F profile extends the initial US GAAP scope without introducing valuation assumptions. SEC identification is local runtime configuration, supplied separately from code. No paid services were introduced.
