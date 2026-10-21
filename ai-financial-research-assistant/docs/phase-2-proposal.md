# Company-name-to-research implementation plan

The user’s updated requirement supersedes the earlier statement-pack proposal: **“I enter a company name. FinSight identifies the company, retrieves its official documents and recent news, analyses the evidence, and produces a useful, cited company-research report.”** The implementation stays in Python/Streamlit, with local caches and replaceable providers. No database, vector store, agent framework, deployment or valuation engine is required.

## Delivered workflow

| Stage | User outcome | Implementation and boundary |
|---|---|---|
| Identify | Search a name/ticker and confirm the legal entity | Official SEC US-listed directory; ambiguous results require selection. Legal name, CIK, ticker/exchange and business-address country. Reporting currency comes only from reviewed extraction profiles; unsupported entities are explicit. |
| Retrieve documents | Inspect the latest annual, subsequent interims and event exhibits | SEC recent filings, bounded exhibit discovery, three reviewed IR landing pages. HTML block/PDF page locations, retrieval time, hash and access status. Scans, inaccessible sources, missing presentations and older archives are explicit gaps. |
| Retrieve news | Review dated company announcements and recent reporting | Adjustable 90-day default, financial-event keyword RSS search, publisher/link/date, source category, duplicate URLs retained. Independent items remain headlines until articles are read; no claim of full-text access. |
| Analyse | Read business descriptions, financial trends, management explanations, developments, risks and research questions | Attributed excerpts plus deterministic calculations; facts, management statements and analyst questions distinguished. Warnings propagate to tables, commentary and exports. Accounting/profile conflicts remain visible. |
| Export | Download a cited report and evidence pack | Markdown, citation/document/news registers, evidence JSON and financial workbook when supported. The research cutoff, news publication window and fiscal periods remain distinct. |
| Optional narrative | Add a model explanation after API setup and explicit spending approval | Replaceable provider, pre-call estimate, cumulative reservation ledger and output-token limit. Exact numerical-record and source-excerpt checks do not establish semantic entailment. Actual provider tokens recorded; billed cost is unknown unless separately established. Disabled by default. |

## Supported scope and quality gates

KSPI, Apple and Microsoft retain reviewed annual financial mappings. KSPI preserves IFRS/KZT, after-rewards revenue, group/parent profit distinctions, and suppression of an industrial-company FCF proxy. Identifying NVIDIA demonstrates broader document research; it does not grant NVIDIA financial extraction coverage. Private or absent listings produce an explicit no-match result.

Tests cover ambiguity, unsupported entities, document locations/scans, date windows, duplicates, stale sources, partial failures, numerical consistency, conflicting observations, warning propagation, exports and model budget controls. Browser acceptance covers all three financial profiles plus NVIDIA, explicit company confirmation and no-match handling. Historical replay is labelled and never masquerades as current retrieval. See [current review validation](review-followup.md) and [earlier validation evidence](research-validation.md).

## Remaining external acceptance and later improvements

1. Apply the saved SEC/news/IR network settings to the running environment, then rerun fresh validation. The 20 October instance starts and passes offline checks but its effective proxy policy lacks these custom domains.
2. Complete native Mac and desktop Excel acceptance. Linux and historical browser replay cannot establish those outcomes.
3. Optional API setup remains a separate user choice. No key, paid service or model charge is necessary for the deterministic report.
4. Broader article/full-text and presentation coverage, custom financial tags, more companies, accounting reconciliation expansion and semantic contradiction detection need dedicated coverage work. Current reports state these limits; do not silently broaden claims.

The implementation is reviewable on the existing feature branch. Do not merge or deploy automatically.
