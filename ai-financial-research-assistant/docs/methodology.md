# Financial methodology and selection policy

## Scope

Live connector: KSPI (CIK 0001985487), consolidated IFRS in KZT via 20-F; AAPL (CIK 0000320193) and MSFT (CIK 0000789019), consolidated US GAAP in USD via 10-K. See [KSPI-specific mapping and controls](kspi-methodology.md). The official ticker directory must agree with the supported CIK. Unsupported companies are rejected. A CSV can describe another company, but remains user-provided, without SEC verification. Coverage is not universal.

## Annual periods and competing values

1. Read `submissions.filings.recent`. Consider the latest five distinct report dates with the profile’s 10-K/10-K/A or 20-F/20-F/A forms. Older submissions archives and quarterly forms are outside this release.
2. For an endpoint, require one unambiguous annual start and fiscal-year label in **its own original annual-report accession's** duration observations. Accept 350–380-day years, including 52/53 weeks; reject short transition periods. No calendar-year assumption is used. Comparative facts' `fy` values are the filing's fiscal year and must not relabel earlier periods.
3. Only the explicit concepts below are considered. Annual durations must match the anchored start **and** end. Instant facts must match the end and have no start. Reject explicit dimensional/segment payloads. CompanyFacts is treated as the consolidated source; custom tags and segment reconstruction are unsupported.
4. Retain all valid matching observations, including original values, source fiscal years, accessions and filing dates. Exact duplicate observations are deduplicated. Unsupported units and malformed observations produce warnings.
5. Within each concept, consider the latest filing date. Same-date conflicting values stay missing. If latest observations across the approved concepts disagree, leave the metric missing. If values agree, prefer the latest date, then the declared concept order, then accession lexical order. This last tie-break affects identical values only.
6. Later differing values produce a competing-values warning. An amended annual filing is labelled explicitly. Later comparative disclosures are labelled. We do **not** infer that every amendment changes financial statements, or that every difference is a confirmed restatement.
7. This is a **latest-available disclosure policy**, not historical point-in-time reconstruction. Analysts must inspect reclassification/accounting-basis changes. Raw values are never adjusted to manufacture comparability.

A missing/ambiguous metric remains missing. Latest-per-metric selection can yield inputs from different filings. Within-period ratios and the cash-flow proxy are suppressed when reported SEC inputs have different accessions; reconcile their basis first. Cross-year growth uses the same revenue concept and currency, consecutive fiscal years, adjacent intervals and annual lengths differing by at most seven days. A 53-week year is flagged; growth is not adjusted for its extra week.

## US GAAP concept mapping (AAPL/MSFT)

| Metric | US GAAP concepts, in preference order |
|---|---|
| Revenue | RevenueFromContractWithCustomerExcludingAssessedTax; SalesRevenueNet |
| Operating profit / loss | OperatingIncomeLoss |
| Net income / loss | NetIncomeLoss |
| Operating cash flow | NetCashProvidedByUsedInOperatingActivities |
| Capital expenditure proxy | PaymentsToAcquirePropertyPlantAndEquipment |
| Cash and equivalents | CashAndCashEquivalentsAtCarryingValue |
| Total assets | Assets |
| Total liabilities | Liabilities |

These tags are not an exhaustive accounting ontology. Revenue concepts are not silently spliced across years. NetIncomeLoss is not automatically substituted with income attributable to common shareholders or another attribution definition. Cash excludes investments and restricted-cash alternatives. PP&E purchases exclude acquisitions and other investments. Missing tags stay missing; no arithmetic reconstruction from differently defined tags is attempted.

## Deterministic arithmetic

- Revenue growth (%) = `(current / previous - 1) × 100`, requiring positive prior revenue and nonnegative current revenue plus comparability controls.
- Operating/net margin (%) = `profit / revenue × 100`, requiring positive revenue; negative profits are valid.
- Cash-flow proxy = `CFO − purchases of PP&E`, with PP&E purchases entered as a **positive outflow**. Negative CFO and negative proxy values are valid. Negative capex is flagged, not silently flipped.
- Margin movement = difference of percentages, expressed in **percentage points**.
- Missing/zero/invalid denominators return no calculated result and an explanatory warning. Missing inputs never become zero.

Decimal arithmetic preserves source amounts and avoids binary-float rounding of input values. Ratios use Python Decimal's normal 28 significant-digit precision; UI/commentary display two places. Charts convert to floats for presentation. CSV retains exact decimals, formula descriptions and input observation IDs. XLSX uses numeric amounts up to 15 significant digits, and rounds percentage calculations to 15 significant digits. Larger-precision source amounts remain text. `exact_value` always preserves the pre-conversion Decimal string; `value_storage` records the decision. No spreadsheet formulas are executed or generated.

For KSPI, operating profit and PP&E-only capex remain missing, and the simple cash-flow proxy is suppressed. IFRS group revenue after rewards, group profit, parent-attributable profit, pretax profit and broader investment purchases are distinct observations. Reported growth includes acquisition/scope effects and is not labelled organic.

Rule-based commentary only describes these results. No unsupported business causes, buy/sell recommendations, generative AI or FCFF valuation claims are produced.
