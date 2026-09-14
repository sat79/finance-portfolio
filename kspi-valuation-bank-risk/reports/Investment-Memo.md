# Kaspi.kz: distribution value and banking risk

Independent portfolio study, 11 September 2026. research and implementation, prepared for Satvik Sahni’s finance portfolio. This is a reproducible analytical exercise with disclosed assumptions, not a current investment recommendation.

## Investment question

How much of a fintech ecosystem’s earnings can reach an ADS holder, and how vulnerable is that value to currency translation, funding costs and credit losses?

## View

Kaspi is a useful test of financial judgement because a bank-backed ecosystem needs a different valuation treatment from a consumer-goods business. Customer deposits are part of funding operations. Subtracting all deposits as conventional corporate net debt after an industrial FCFF valuation would misstate the economics. This study instead values assumed distributions to equity and uses an earnings multiple only as a separate cross-check.

The base dividend scenario produces **$73.11 per ADS**. Downside and upside assumptions produce **$45.53 and $95.68**. These are model outputs, not observed prices or price targets. The assumed 10× FY2025 diluted earnings cross-check gives **$116.33** at reference FX. The gap is a reason to investigate payout, reinvestment and discount assumptions; averaging the two would hide that disagreement.

## Data and method

The source register links the FY2025 Form 20-F and the 2Q2026 release. The model uses a KZT1,000 proposed quarterly distribution as a starting assumption, annualised to KZT4,000. Each of five annual distributions is grown in KZT, translated using a separate FX path and discounted at an illustrative USD cost of equity of **13.55%** (4% risk-free + 1.1 beta × 5.5% ERP + 3.5% additional premium).

Terminal growth is currency-consistent: `(1 + KZT dividend growth) / (1 + KZT depreciation) − 1`. Five per cent local dividend growth and four per cent depreciation imply approximately 0.96% USD growth. The terminal component contributes **56.2%** of base value. Cash flows occur at the end of five 12-month periods from the valuation date; there is no calendar-year stub calculation.

The model retains FY2025 diluted EPS separately for the multiple cross-check. It does not treat the June FX reference as today’s exchange rate, the proposed distribution as a guaranteed dividend, or historical EPS as a forward forecast.

## Credit and funding sensitivity

With static disclosed average balances, an additional 100 basis points of annual funding cost and 100 basis points of annual credit loss produce a combined **KZT151bn pretax** earnings reduction. At an assumed 25% tax rate, the effect is **KZT113.25bn**, or **11.1%** of twice H1 group net income. Annualising H1 income provides scale only; it is not an earnings forecast.

This deliberately simple calculation exposes the transmission mechanism. It assumes all savings reprice immediately for a year and uses net loans as a proxy for credit exposure. It omits repricing lags, customer behaviour, balance growth, defaults over time and interactions. It is neither regulatory stress testing nor IFRS 9 ECL.

## SQL analysis and accounting controls

The supplied SQL compares segment revenue growth, earnings growth and margins for FY2024 and FY2025. A composite key prevents duplicate segment-years. The Python runner reconciles segment net income to group net income and independently reproduces the Excel dividend outputs. Acquisition effects make Marketplace growth unsuitable as a proxy for organic growth. Segment revenues precede consolidation adjustments; they must not simply be labelled group revenue.

## What would change the view?

- A distribution policy that retains more cash than assumed would reduce dividend value even if earnings grow.
- Faster currency depreciation would reduce translated distributions; a higher required return would reduce present value.
- Funding costs rising faster than asset yields could depress near-term profitability.
- Faster loan growth without matching underwriting and collections capacity would weaken the risk-adjusted growth argument.
- A more favourable operating outlook in Türkiye would need evidence of returns after investment and funding requirements, rather than a revenue-only narrative.

## Limitations and next analytical extension

This is a completed first-stage valuation exercise, not a full coverage initiation. It has no independently calibrated beta, observed peer-multiple set, current share-price comparison, consolidated three-statement forecast, regulatory capital model or segment cash-flow valuation. Those are the most useful extensions. Start with capital and distributable-cash constraints, then reconcile a segment valuation to attributable equity without double-counting the bank’s funding liabilities.

The original analyst must understand and challenge the work before discussing it in an interview. The project demonstrates an analytical workflow, not independent verification of the portfolio owner’s unaided coding ability.


## What the segment comparison adds

The SQL separates revenue growth from profit conversion. On the reported basis, Fintech revenue grew 20.4% while segment net income grew 8.6%; Payments net income grew 13.5%. Marketplace revenue growth of 163.5% coincided with a 19.7% fall in segment net income. Acquisition effects prevent interpreting the latter as organic growth. These calculations point to different diligence questions: funding and credit costs for Fintech, and integration costs, investment and profitability for Marketplace. They do not establish causation.

For a lending decision, the next step is to connect expected losses and funding costs to pricing, customer acquisition costs and capital consumption. A stock-level dividend model cannot answer loan-level underwriting questions by itself.

[Review the calculation checks](Validation.md). The code, model and data can be inspected and run locally.

## Strategy update — 13 September 2026

[Read the super-app and Türkiye thesis](Super-App-and-Turkiye-Thesis.md). This extension distinguishes established operating performance from international execution risk, checks engagement terminology and adds a reproducible geographic profit comparison. The dividend valuation has not been increased on the strength of a narrative alone.
