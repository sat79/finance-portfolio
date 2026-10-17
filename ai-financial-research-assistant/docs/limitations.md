# Current limitations and operating costs

- **Phase 1 acceptance remains open:** external SEC access is blocked in the development environment. Apple/Microsoft historical data have not been retrieved or reconciled here. No synthetic test is evidence of live financial accuracy.
- Initial live scope is two US GAAP operating companies, USD, supported standard concepts and recent annual filings. No banks, insurance, IFRS, segments, custom tags, quarterly analysis, transition-year handling, FX conversion or universal coverage.
- Latest available observations can contain later revisions. This is not a historical point-in-time database. Annual/accounting comparability still needs human judgment. Source links identify filing indexes, not invented document pages.
- CSV is unverified user data. A plausible reference or CIK is not evidence of authenticity. Uploaded data are held in Streamlit session memory, not written to the app cache or transmitted to AI services. Clear the session when done; this is not a hardened multi-tenant document platform.
- Public SEC JSON is cached for up to 24 hours, with retrieval timestamps and hashes. An expired cache is not used when a refresh fails. The cache has no automatic disk quota/eviction; a deployment needs storage management.
- Rate limiting is process-wide (1 request/second). Several app processes or users sharing egress require aggregate coordination. Redirects and arbitrary URLs are rejected. Network calls have timeouts, bounded retries and a 25 MiB response limit.
- Spreadsheet exports escape formula-like text. No macros/formulas are generated. Amount strings retain precision; users must convert selected numeric columns in Excel when needed.
- Python 3.12.14/Linux was tested. Intel macOS and Colab installation instructions are provided but not claimed as executed. A browser smoke test is local Chromium, not deployment or mobile validation.
- No AI, valuation engine, recommendations, login, persistence database, hosting, financial transactions or paid resources are implemented. The product's AI working name describes future scope, not present functionality.
- No licence is added. Official SEC access/fair-use and redistribution documentation could not be fetched in this environment. Verify current terms before public hosting or redistributing real-company datasets; none are bundled here.

## Cost

Local Python, Streamlit, deterministic calculations, CSVs and exports have no service charges. The design uses public SEC endpoints without a paid financial-data or LLM API. No billable resources have been provisioned. Hosting and future LLM costs are outside this milestone and require a separate decision.
