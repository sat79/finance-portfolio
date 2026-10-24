# Kaspi.kz — analytical review of the fresh research report

Research cutoff: **2026-10-23T02:12:41.147537+00:00** (03:12 BST, 23 October 2026). This is an analyst review of the supplied source evidence, not paid-model output, independent verification or an investment recommendation. Read it alongside the complete `research-report.md` inside the review package (also provided separately as `KSPI-full-report.md`) and the original `KSPI-evidence.zip`. The automated report is retained unchanged. Additional source passages used here are explicitly registered in `review-citations.json`; they were in the retrieved documents but some were omitted from the automated report/model selection.

**Assessment:** the report is a useful, auditable evidence pack, but its deterministic passage ranking is not yet a strong investment-research synthesis. The most useful question is why reported revenue growth is substantially stronger than profit growth, and whether funding pressure, acquisition mix and credit risk explain that difference. The evidence below supports investigating that question; it does not fully quantify the causes or justify a valuation.

## Coverage and period boundaries

| Coverage | Fresh result | Limit |
|---|---|---|
| Official documents | 21/21 registered documents read, including the IR landing page; 20 substantive documents | Bounded SEC/IR discovery, not proof that every presentation or subsequent development was found |
| Financial extraction | 27 selected annual observations; FY2023–FY2025, IFRS/KZT | Reviewed extraction covers **KSPI, AAPL and MSFT only**; recent quarterly/YTD amounts remain attributed source text |
| Independent news | Guardian banking feed fetched; **no matching Kaspi article** in 26 July–23 October window | No network or body-extraction failure; Google headlines remain discovery-only. No inference of “no material news” |

The annual baseline ends 31 December 2025. The earnings release covers **2Q and 1H ended 30 June 2026**, published 10 August. Its “2Q 2026 Highlights” heading establishes the scope of the quarterly bullets below; the publication/current-report date is not the period end. The interim credit-risk amounts are **balance-sheet stocks at two dates**, not quarterly or YTD flows. September shareholder resolutions are events, not financial reporting periods. [E7:B4](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B5](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E5:B2151](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000026/kspi-ex99_1.htm) [E3:B4](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm)

## Material findings, evidence and interpretation

### 1. Reported annual growth does not translate into comparable profit growth

**Reported facts:** consolidated after-rewards revenue rose from KZT2,532.156bn in FY2024 to KZT4,046.074bn in FY2025. Group net income was KZT1,056.834bn and KZT1,067.707bn respectively. These are group figures, not income attributable to parent shareholders. [Fcca88fe8bd6a79f4c722](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/0001985487-26-000008-index.html) [F41c1bef463b894b62aa0](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/0001985487-26-000008-index.html) [F45938352051ff703ee85](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/0001985487-26-000008-index.html) [Fd263c4ad59b3d9845882](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/0001985487-26-000008-index.html)

**Calculations:** reported revenue growth is **59.79%**; group net-income growth is **1.03%**. Group net margin is **41.74% → 26.39%** (`net_income / revenue`). Exact Decimal values, formulas and input citations are in `review-calculations.json`. No interim amount enters this arithmetic.

**Management explanation:** the annual disclosure says costs and operating expenses increased 117%, “primarily due to acquisition of Hepsiburada, growth in interest expenses and fees”. It reports Türkiye costs/operating expenses of KZT1,108,903 million. [D1:B2312](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/kspi-20251231.htm)

**Interpretation, unverified:** acquisition/business mix and funding costs are plausible contributors to weaker profit conversion. The data do **not** establish organic growth or isolate how much margin change each cause explains. The report correctly retains Hepsiburada/IAS 29 and revenue-definition warnings, but does not build a quantified comparable-scope bridge. That bridge is the main missing analytical work.

### 2. The latest quarter carries the same revenue-versus-profit tension

**Reported facts / management explanation:** under the 2Q highlights heading, the release reports revenue up 15% year-on-year to KZT1.1tn, adjusted EBITDA up 5% to KZT397bn, and net income stable at KZT259bn “even with investments in Türkiye and high funding costs in Kazakhstan.” These are management's quarterly disclosures, not newly normalized annual observations. Adjusted EBITDA is a management measure, not IFRS operating profit. [E7:B5](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B24](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm)

**Interpretation, unverified:** the quarter suggests that stronger activity is not yet producing proportionate group earnings growth. It does not prove a persistent trend or a forecast. The automated report misses this consolidated highlight while selecting lower-priority accounting-policy text; a reviewer should read this paragraph before the generic conclusion.

### 3. e-Commerce is the disclosed growth driver; do not mix growth bases

**Reported facts:** management calls e-Commerce the main growth driver. For 2Q it reports constant-currency GMV growth of 28% and purchase growth of 33%; the next bullet reports constant-currency e-Commerce revenue growth of 35% and VAS revenue growth of 49%, with a 3P take rate of 16.1%, up 160bps. By contrast, the Marketplace bullet reports revenue growth of 11% on a **reported** basis. [E7:B5](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B9](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B11](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B15](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm)

**Interpretation, unverified:** monetization appears to matter alongside volume. Advertising/delivery economics and Türkiye integration deserve attention, but constant-currency e-Commerce and reported Marketplace growth cannot be used as a like-for-like comparison. GMV is not revenue. These useful operating details are present in the retrieved evidence but not prioritized by the automated report.

### 4. Funding, payment mix and credit quality need targeted risk review

**Reported facts / explanations:** Fintech revenue grew 23% while adjusted EBITDA grew 6%; management cites higher funding costs. Payments TPV grew 13%, revenue grew 5%, and adjusted EBITDA was broadly stable; management cites pay-by-palm investment, and attributes the take-rate move from 1.07% to 1.00% to product mix. The release separately says the rate on the three-month deposit product was reduced by 100bps in August and that the product represented around one-third of deposits. This later pricing action is not an observed June-quarter benefit. [E7:B17](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B19](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B22](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E7:B80](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm)

**Reported interim risk fact:** restructured loans in Stage 3 had gross carrying amounts of KZT145,302 million at 31 December 2025 and KZT178,567 million at 30 June 2026. This is a specific subset of loans, **not** total NPLs, total expected credit losses or a loan-loss rate. [E5:B2151](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000026/kspi-ex99_1.htm)

**Interpretation / unresolved questions:** does lower deposit pricing reduce funding costs after allowing for repricing lags, volumes and asset yields? What explains the Stage 3 restructured-loan movement, and what are its coverage, recoveries and share of the loan book? The automated report's broad risk boilerplate does not answer these questions. The interim document says the bank monitors Basel III capital adequacy, but that statement alone proves neither sufficient capital headroom nor distributable parent cash. [E5:B2765](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000026/kspi-ex99_1.htm)

### 5. Distinguish a dividend proposal from the later approval

**Reported chronology:** the August release proposed KZT1,000 **per ADS**, subject to shareholder approval. The September disclosure says resolutions passed on **9 September**, approves KZT1,000 **per common share** for 2Q2026, and states commencement of payments on 9 September with an 8 September record date. Preserve those instrument labels; do not silently assume the ADS conversion ratio. [E7:B7](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000024/kspi-ex99_1.htm) [E3:B4](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm) [E3:B12](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm) [E3:B14](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm) [E3:B16](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm) [E3:B18](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm) [E3:B20](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000028/kspi-ex99_1.htm)

**Interpretation / limit:** this supports a proposal-to-approval chronology, not proof that an individual holder received cash. Sustainability still needs parent liquidity, regulatory distribution capacity, credit losses and investment commitments. Consolidated bank operating cash flow is not distributable cash; the existing suppression of the industrial CFO-minus-PP&E proxy is appropriate.

## Critique of the automated report

- **Materiality:** useful data and warnings are retained, but repeated business descriptions, accounting-policy passages and long warning-filled tables obscure the key revenue/profit divergence, operating drivers and credit questions. The report needs a short ranked synthesis, not more data sources before it can be useful.
- **Explanations:** annual management explanations are attributed and separated from newer periods, which is correct. The narrative still lacks a quantified bridge between acquisition/scope effects, funding costs and comparable underlying performance. It must not fill that gap with a plausible-sounding causal story.
- **Periods:** annual calculations are auditable and quarterly/YTD amounts are not annualized. Some excerpts omit their nearby headings, leaving period cues unresolved. The review above binds the quarterly bullets to the explicit 2Q heading rather than treating a filing date as a financial period.
- **Financial risks:** the bank cash-flow and profit-definition safeguards are useful. Credit quality, capital, funding repricing, Türkiye/IAS 29 effects and parent cash need prioritized analysis. The Stage 3 subset is an example of material evidence the generic risk selector overlooked.
- **Recent developments:** the dividend chronology can be traced to official sources. Kasper/product announcements are management-reported adoption, not independently verified economics. Kaspi independent-news coverage remains absent despite a successful feed request. Headline-only valuation or regulatory stories must not support conclusions.
- **Conclusion:** good enough to start an evidence-led review; not yet sufficient to support valuation, a forecast or an investment decision. The critique is separate from the automated report and has its own source register; it is not an evaluated automated synthesis capability.

## Five questions to resolve before valuation

1. What is the comparable-scope, constant-currency revenue/profit bridge excluding acquisition and IAS 29 effects?
2. How much of the funding-rate change is realized in subsequent earnings, and at what deposit/loan volumes and yields?
3. What drives the restructured Stage 3 increase, and how does it compare with total credit exposures and coverage?
4. What capital and parent-level cash support dividends after credit losses, Türkiye investment and regulatory limits?
5. Which recent developments can be corroborated independently, and which remain management-only claims?

No paid model call was made. A bounded, disabled synthesis-pilot specification and price-scenario estimate accompany this review; it is optional and has not been executed.
