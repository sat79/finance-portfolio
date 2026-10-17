# Phase 1 quality review — 17 October 2026

Reviewed the existing implementation as an accounting-data workflow and as a Python application. This was a separate review pass by the development assistant, not an external audit. The existing feature branch and PR #1 were inspected before edits: four feature commits, open/unmerged PR, two green GitHub checks, 80 passing local tests, and a clean tracked worktree. The pre-existing untracked market CSV in another project was left alone. No unfinished Git operation was found. Existing Streamlit services were present; fresh checks used separate owned services on ports 8503/8504.

## Findings and disposition

| Severity | Finding | Disposition and evidence |
|---|---|---|
| Medium — analytical usability | XLSX stored all financial values as text, obstructing modelling | Fixed. Ordinary amounts are numeric; repeating percentage calculations rounded to 15 significant digits; exact Decimal backups and storage labels added. Unsafe high-precision amounts remain text. Boundary, negative, missing, identifier and all-three-company workbook regressions pass. |
| Medium — misleading financial presentation | An unverified CSV with KSPI's CIK inherited a verified-sounding “consolidated IFRS revenue after rewards” label | Fixed. That claim now requires SEC-origin data. KSPI CSV explicitly requires revenue/profit-definition review; financial-group FCF suppression still applies. AppTest reproduces and guards the distinction. |
| Medium — reliability | Invisible control/XML-invalid characters could pass CSV validation and crash XLSX generation, which is prepared during app rendering | Fixed. Unsupported characters are rejected with an actionable import error. Five character regressions added; quoted tabs/newlines remain supported and formula-like names remain escaped. |
| Low — clarity | Chart captions did not name the currency or explicitly label percentage trends | Fixed. Financial charts name USD/KZT (as supplied); ratio chart says %. Presentation only; no change to calculations. |
| Medium — evidence limitation | 48-value reconciliation covers duration metrics, not every displayed figure or earlier year | Remains explicit. Reproduced all 48 matches against hash-checked filed XBRL, compared fresh exported data to the historical sample, and spot-checked rendered statement text. No claim of universal correctness. |
| Medium — environment reproducibility | Saved configuration referenced main, while install/start instructions assumed unmerged feature files | Configuration inspected; final repository snapshot/setup instructions are handled through the onboarding draft. Publishing/restoring is a separate environment operation, not proven by local app tests. See final task report for save result. |
| Medium — platform acceptance | No actual Intel Mac/desktop Excel runtime available here | Added exact Mac guide and unchecked acceptance test. Intel macOS 12 and 14 wheel downloads succeeded; Linux launcher/browser/workbook checks passed. Native Mac and Excel acceptance remains outstanding. |

The new regressions were run before fixes: 13 failures reproduced the value-cell, invalid-character and KSPI-label issues. After the fixes and extra safety/company checks, the full suite reports **102 passed**. Existing tests were retained; no accounting assertion was relaxed. No critical or high-severity defect was established within the reviewed scope. This is not a security certification.

## Financial review

- **Periods and fiscal years:** selectors use original annual accessions to anchor exact 350–380-day intervals and FY labels; later comparative `fy` metadata is retained separately. Apple September, Microsoft June and KSPI December year-ends are preserved. Quarter/dimensional observations are excluded, 53-week years flagged, and stub years remain unsupported. Revenue growth requires consecutive compatible periods; no calendar-year conversion is performed.
- **Revisions and concepts:** latest compatible observations are selected; originals/competitors remain inspectable. Same-date and concept conflicts stay missing. Amendments and later comparative disclosures generate warnings. This is not point-in-time historical data. Different-filing inputs suppress same-period ratios; cross-year comparability still requires review of revisions and accounting scope.
- **Definitions:** US GAAP operating income and revenue mappings remain distinct from KSPI's IFRS profile. KSPI after-rewards revenue, group profit, parent-attributable profit, pretax profit and broad purchases stay separate. Apple's and Microsoft's shared US GAAP definitions do not imply identical fiscal calendars. No additional company was enabled.
- **Signs and cash flow:** losses/negative CFO are valid. PP&E purchases use positive outflows before subtraction. A negative supplied purchase amount is rejected; a negative reported capex cannot produce a cash-flow proxy without review. KSPI generic FCF is always suppressed, including known-KSPI CSVs. CFO is not distributable bank cash.
- **Missing values/units:** missing inputs remain missing, never zero-filled. Whole reported currency units are used internally; chart millions are display scaling only. Ratio inputs require consistent units/currencies. KSPI's USD convenience translation is excluded in favour of KZT.
- **Ratios/provenance:** calculations carry input IDs, formulas and warnings separately from reported facts. Margin changes use percentage points, not percentage growth. Links identify real filing indexes, not fabricated pages. CSV and fictional data never acquire verified source URLs.

Rendered filing text was spot-checked separately from the selector: Apple's FY2025 net sales/operating income and parenthesised PP&E purchases; Microsoft's FY2026 revenue/operating income; KSPI's FY2025 revenue/rewards and group/parent profit including the NCI loss. These checks support the documented historical examples. They do not verify all notes, balance-sheet figures, acquisition accounting or IAS 29 adjustments independently.

## Software and usability review

The architecture remains small: validated source records → deterministic selection/calculations → Streamlit presentation and exports. Decimal arithmetic is retained throughout the analytical layer. XLSX conversion is confined to the exporter; CSV and source data remain exact. No extra framework or service was introduced.

Transport restricts requests to supported official SEC endpoints, verifies ticker identities, rejects redirects, identifies requests, throttles to one request/second per process, bounds retries/timeouts and caps responses at 25 MiB. JSON duplicate keys/non-finite values are rejected. Cache entries are hash-checked, dated and atomically replaced; expired/corrupt cache never silently substitutes stale data. Public JSON alone is cached. CSV uploads stay in session memory; text fields are escaped in spreadsheets. No shell is used on user uploads and no formulas/macros are generated.

Reviewed error paths include configuration errors, denied/timed-out requests, malformed data, missing metrics, bad uploads and export precision. The browser flow covers company selection, loading, tables, ratios, sources, warnings and downloads. Disk cache has no quota, multiple app processes do not share a rate limiter, and no multi-user/security-hardening or load test was performed. Those are limits of a local MVP. Dependency pins and `pip check` were verified, but no independent vulnerability scan was performed; pinning is not a vulnerability guarantee.

The two UI items described as **“Needs attention”** were not exposed by the available configuration-read tool, and no Page was visible in this chat. The draft exposed no pending runtime requirements, but that does not establish what those two badges mean or that they are resolved. Configuration save/publication and fresh-task restoration must not be inferred from a green application test.

## Remaining priorities

1. Complete the user's Mac/Chrome/Excel acceptance checklist; native runtime and desktop recalculation are untested here.
2. Improve reconciliation coverage and visible review status before adding analytical breadth. See the [ranked Phase 2 proposal](phase-2-proposal.md); it is not implemented.
3. Retain explicit limits on revisions, unsupported tags, short years, bank cash-flow interpretation, cross-company comparability and multi-process operation.

No Phase 3/4, valuation, paid API, deployment or merge was performed. Existing notebook and unrelated portfolio projects are preserved.
