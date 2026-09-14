# Source register

Accessed 11 September 2026. Inputs are fixed historical extracts, not live feeds.

- [Kaspi.kz Form 20-F 2025](https://ir.kaspi.kz/media/Form_20-F_2025.pdf): PDF p1 ADS ratio; p104–106 segment figures; p159 consolidated earnings; p188 segment reconciliation; p196 diluted EPS. Figures in the CSV are KZT millions. FY2025 includes Hepsiburada acquisition effects and is not a like-for-like organic growth series.
- [2Q and 1H2026 results](https://ir.kaspi.kz/media/2Q_2026_Results.pdf): PDF p1 proposed quarterly dividend; p11 rounded loan/savings balances and NPL ratios; p14 H1 group earnings; p18 reference FX. The dividend was described as proposed in this release; subsequent approval has not been checked.

Assumptions, rather than sourced observations: all dividend-growth paths, FX-depreciation paths, USD risk-free rate, beta, ERP, additional premium, selected P/E, stress sizes and tax rate. The valuation uses June reference FX and FY2025 EPS as explicitly labelled inputs. A current investment decision would require current market data and refreshed forward earnings.

`group_income_controls.json` records consolidated group net income, not net income attributable to shareholders, for FY2024 and FY2025 in KZT millions. Both controls are from the consolidated statements in the FY2025 Form 20-F (PDF p159).

## Strategy extension — checked 13 September 2026

`geography.csv` transcribes FY2025 Form 20-F PDF p189 (printed F-35). The extract preserves the reported “Kazakhstan & Other” scope, group net income and missing consolidated Turkish 2024 comparison. Engagement definitions and values are on PDF p51. The new research note contains the interview-source review and latest Türkiye strategy references. `src/analyse_geography.py` reconciles the geographic income totals with the existing group controls before calculating growth.
