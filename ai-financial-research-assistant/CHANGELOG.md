# Changelog

## Phase 1 quality and usability review — 17 October 2026

- Numeric XLSX value cells with 15-significant-digit safeguards, exact Decimal backups, explicit storage labels, preserved text identifiers and formula-injection protection.
- Rejected CSV control/XML characters that could crash exports; stopped unverified KSPI CSVs inheriting SEC-specific accounting-basis claims.
- Named currencies/percentage units in chart captions; retained KSPI's financial-group controls.
- Added a local startup helper, Intel Mac guide, unchecked three-company/Excel acceptance checklist, quality-review findings and ranked Phase 2 proposal.
- Validation increased from 80 to 102 passing tests; fresh SEC retrieval and the 48-value historical reconciliation repeated; browser checks now inspect numeric XLSX downloads for all three companies. No native Mac or desktop Excel execution claimed.

## 0.1.0 — 17 October 2026 — scoped research MVP, review candidate

- Audited existing financial projects and preserved the learning notebook.
- Added typed source observations, annual SEC filing selection, explicit revision/ambiguity controls, deterministic financial ratios and provenance links.
- Added SEC ticker/CompanyFacts/submissions connector with cache, identification, bounded network requests and explicit errors. Scope: KSPI/AAPL/MSFT. Live retrieval returned three KSPI periods and five each for Apple/Microsoft. Forty-eight financial facts across three periods per company matched standalone filing XBRL.
- Added validated CSV preview/import, a fictional example, Streamlit research workflow, charts, observations and CSV/XLSX exports.
- Added offline arithmetic, schema, selection, transport, export and UI tests plus an optional browser smoke script and a live evidence script.
- Added methodology, schema, limits, learning exercises and a completed sample reconciliation register. No licence, LLM, paid service, valuation engine or deployment added.

See `docs/validation.md` for actual execution evidence and outstanding acceptance criteria.

- Added the user-requested KSPI default: IFRS/KZT/20-F, revenue after rewards, separate profit attribution and investment purchases, and suppression of the generic bank cash-flow proxy.
