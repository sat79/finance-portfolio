# Proposed Phase 2 — not authorised for implementation

The strongest next milestone is **a reviewed annual statement pack for KSPI, Apple and Microsoft**, with wider financial coverage and explicit reconciliation status. Analysts first need to know whether figures add up, use compatible definitions and have been reviewed. That adds more value now than generating fluent commentary over a narrow, partly checked dataset.

The following ranking assumes the current three-company scope, local operation and no paid services. Complexity is relative engineering/review effort, not a promised delivery date. Costs exclude the user's existing computer and analyst time.

| Rank | Option | Business usefulness | Complexity | Accuracy risk | External cost | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Better SEC reconciliation and visible review status | Very high: distinguishes verified figures, unresolved conflicts and missing data before use | Medium | Medium: source definitions and amendments still require judgment | £0 using public sources | Core next milestone |
| 2 | More complete financial statements | Very high: enables meaningful liquidity, capital and cash-flow analysis | Medium–high | High: IFRS/US GAAP, bank cash flows and taxonomy mappings differ | £0 | Add a small reviewed set alongside reconciliation |
| 3 | Financial analysis and downloadable research report | High: converts reviewed data into a useful analyst deliverable | Medium | Medium: qualitative conclusions can overstate what ratios establish | £0 with deterministic templates | Start with a concise factual statement pack; no invented causes |
| 4 | Company comparisons | Medium now: Apple and Microsoft can be compared with fiscal-period caveats | Medium | High if dates, currencies or KSPI's business/accounting basis are flattened | £0 without FX provider | After consistent definitions and reviewed periods; KSPI in a distinct comparison context |
| 5 | Financial document ingestion | Potentially high: reaches notes and custom disclosures absent from CompanyFacts | High | High: extraction errors, tables, units and page provenance | £0 for local parsing, substantial review effort | Separate later milestone; do not start in this task |
| 6 | Source-backed AI research | Potentially high for answering questions about verified sources | High | High: hallucinations, retrieval misses and unsupported inference need evaluations | Variable; free local models also impose compute/quality tradeoffs | Only after a source corpus and evaluated citations; no API provisioned |

## Suggested bounded scope for approval

1. Keep all three companies, separate definitions and reported currencies. Add explicit **unreviewed / matched / conflicting / unavailable** states at metric and period level. Keep reported values immutable and store any analyst decisions separately with their source and rationale.
2. Expand only the fields needed for two useful reconciliation paths: balance-sheet totals/equity (including non-controlling interests) and the cash-flow reconciliation. Document restricted cash, FX and other reconciling items before applying a cash movement identity. Do not force an identity by filling gaps with zero.
3. Establish expected accounting identities and tolerances from each filing's stated rounding. Retain custom-tag or unsupported gaps as review items. For KSPI, preserve group/parent distinctions and banking-specific capital/liquidity interpretation; no conventional distributable-FCF assumption.
4. Export a compact statement pack with source links, selected filing versions, reconciliation results, unresolved items and deterministic ratios. Human review remains explicit; downloading or passing a test does not approve the accounting.

## Completion criteria

- A reviewed mapping register names the source concepts, definitions, fiscal periods and limitations for every added field.
- At least three annual periods per company have independently read source evidence for the new coverage; conflicts remain visible.
- Regression fixtures include amended filings, missing reconciling items and different reporting units. Numerical identities do not pass merely because totals were copied from one another.
- The user can trace, review and export one statement pack per company on their Mac, with acceptance recorded by the user.
- Existing 102 tests, XLSX precision/safety checks and KSPI controls continue to pass. No new company, AI, valuation, document-ingestion pipeline, paid service or deployment is included.

This is a proposal only. Start it after the user's approval, ideally after completing the [Phase 1 acceptance checklist](acceptance-test.md).
