# AURA: financial inclusion beyond technical efficiency
A portfolio derivative of Satvik Sahni's supplied MSc dissertation, with a new quantitative audit extension. The original documents are unchanged.

## Research question
When do lower transaction costs translate into a useful financial service for underserved customers?

The dissertation proposes AURA: Accessibility, Usability, Reliability and Affordability. It combines secondary literature, synthetic personas, implementation discussions and simulation assumptions. Its most defensible contribution is a structured way to ask customer-outcome questions; empirical validation and novelty beyond this work are not established by the supplied materials.

## A practical decision framework
| Dimension | Decision question | Evidence to collect in a pilot |
| --- | --- | --- |
| Accessibility | Who is excluded before onboarding? | Completion and drop-off by device, language and access needs; assisted-channel availability |
| Usability | Can a customer understand and complete the task? | Observed task completion, errors and comprehension, with documented consent |
| Reliability | Can customers obtain help and recover from failure? | Failed transactions, recovery time, complaints and resolution |
| Affordability | Is the service cheaper after all adoption costs? | Fees, device/data costs, time costs and comparison with available alternatives |

These are proposed measures, not measured outcomes. Consumer vulnerability and outcome monitoring offer a useful connection to banking product decisions without asserting regulatory compliance.

## What the new code establishes
| Context | Recomputed /100 | Reported rounded | First among sampled weights |
| --- | --- | --- | --- |
| Kenya context | 79.4 | 79 | 74.85% |
| Indonesia context | 66.1 | 66 | 0.00% |
| Argentina context | 76.9 | 77 | 25.15% |

The totals are arithmetically consistent after rounding. The original scores lack supplied source-level measurements and a complete rubric for intermediate scores. Therefore the table is an audit of supplied illustrative numbers, not a ranking of actual services. With 10,000 Dirichlet(1,1,1,1) preference draws, the top-ranked context changes; this is sensitivity to one arbitrary weighting distribution, not statistical validation.

| Region | 10-year midpoint | Parameter-corner range |
| --- | --- | --- |
| Sub-Saharan Africa | 15.4% | 5.5%–29.3% |
| Southeast Asia | 24.6% | 12.7%–40.3% |
| Latin America | 11.6% | 3.9%–24.8% |

The Bass formula is F(t)=m×(1−exp(−(p+q)t))/(1+(q/p)exp(−(p+q)t)). Assuming annual coefficients, the final document's parameter ranges do not support a universal statement of 25–65% adoption by years 6–10. Market ceiling m is an asymptote, not necessarily adoption reached by year ten. The original table's time units need confirmation; the ranges above are parameter-corner scenarios, not confidence intervals.

The stated fall from 12.3% transaction cost to 4.2–8.7% implies a **29.3–65.9%** relative reduction, rather than the stated 35–65% range. This corrects arithmetic; it does not verify any of the input cost estimates.

## Evidence boundary
No original simulation code, seed, raw draws, interview records, participant dataset or scoring measurement register was supplied. This extension does not recreate the original 10,000-iteration Monte Carlo results. Persona dialogue should be labelled illustrative composite language unless exact published quotations can be verified. No claim of field interviews, measured borrower savings or validated AURA performance is made in this portfolio derivative.

The original case-study performance numbers are excluded from the portfolio summary pending source-by-source verification. Future Mali fieldwork described in the dissertation is a proposal, not completed research.

## Best next step
Create a source register and full scoring rubric, then run a small consented usability study with predefined outcomes and independent scoring. Test total cost including onboarding and device costs. Compare a conventional digital service with a blockchain-enabled alternative under the same customer conditions. Keep simulation uncertainty separate from sampling uncertainty and real-world treatment effects.
