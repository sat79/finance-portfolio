# Kaspi.kz: IFRS, KZT and financial-group controls

KSPI is supported alongside AAPL and MSFT and is the default company selection. CIK: **0001985487**. It files **20-F** annual reports, uses **IFRS**, and reports consolidated financial statements in **KZT**. The application does not convert these figures to USD or compare their nominal amounts with Apple/Microsoft.

## Revenue after customer rewards

Use `ifrs-full:Revenue`, the revenue line in the consolidated income statement. It differs from **segment revenue before rewards** used in the older `kspi-valuation-bank-risk` study. Neither definition is silently relabelled as the other.

Verified bridge from the [FY2025 20-F](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/kspi-20251231.htm), revenue note (printed F-32/F-33), in **KZT millions**:

| Fiscal year | Segment revenue | Customer rewards deducted | Consolidated IFRS revenue |
|---|---:|---:|---:|
| 2023 | 1,953,068 | 39,578 | 1,913,490 |
| 2024 | 2,586,381 | 54,225 | 2,532,156 |
| 2025 | 4,101,961 | 55,887 | 4,046,074 |

The prior portfolio's segment/geographic revenue basis is preserved. This new app's reported revenue growth and net margin use consolidated revenue **after rewards**. FY2025 includes Hepsiburada and IAS 29 effects; reported growth is not organic, acquisition-adjusted or constant-currency growth.

## Reviewed concept mapping

| Metric | IFRS concept | Treatment |
|---|---|---|
| Consolidated revenue | Revenue | After customer rewards |
| Group net income | ProfitLoss | Includes non-controlling interests |
| Parent-attributable profit | ProfitLossAttributableToOwnersOfParent | Separate from group income |
| Profit before tax | ProfitLossBeforeTax | Never substituted for operating profit |
| Operating cash flow | CashFlowsFromUsedInOperatingActivities | Lending/deposit movements affect this measure |
| Cash | CashAndCashEquivalents | Year-end instant |
| Assets / liabilities | Assets / Liabilities | Year-end instants |
| Broader investment purchases | PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets | Filing line: purchase of property, equipment and intangible assets; positive outflow, distinct from PP&E-only capex |
| Operating profit / PP&E-only capex | No reviewed standalone standard concept in this profile | Explicit missing state; no estimation |

No US GAAP tag or USD observation is substituted into KSPI's IFRS/KZT profile. An unexpected unit produces a warning and is excluded.

## Ratios and interpretation

The app calculates reported revenue growth and **group net margin** using aligned, compatible observations. For FY2025, `1,067,707 / 4,046,074 × 100 = 26.3887%` net margin. Profit attributable to owners is 1,073,177 million KZT; it exceeds group income because non-controlling interests made a loss. This is not treated as invalid data.

Operating margin remains unavailable. The generic CFO less PP&E cash-flow proxy is **suppressed** for this financial group even when a CSV supplies a capex value. Bank lending, deposits, funding and regulatory capital mean this shortcut must not be represented as distributable cash or FCFF. The broader investment-purchases line remains visible for source inspection.

This milestone does not calculate regulatory capital, NPL ratios, funding spreads, cost of risk, dividend capacity or a KSPI valuation. The older dividend model remains a separate assumptions-based study. Segments and the rewards bridge above are documented evidence; there is no automated segment-analysis dashboard in this release.

## Verification

The app retrieved FY2023–2025 from the official SEC APIs. Eighteen duration observations—six metrics across three years—were reconciled to the separately downloaded FY2025 filed XBRL instance: revenue, group income, parent-attributable income, pretax profit, CFO and broader investment purchases. All differences were zero. The reconciliation register records actual contexts, source hashes and URLs. Cash/assets/liabilities are traceable API observations but outside that independent 18-value sample.

The frozen KSPI CompanyFacts/submissions subsets support regression testing; they are labelled dated official-data extracts, not live results. No complete filing or full API dataset is redistributed.
