# Learning Log

Use this journal to track skills you can genuinely explain and demonstrate in an interview.

## Phase 1 — Lesson 01

- [ ] Open the notebook in Google Colab.
- [ ] Run all cells successfully.
- [ ] Explain what a Python variable and a function do.
- [ ] Explain the difference between revenue growth and operating margin.
- [ ] Change the fictional 2024 revenue to 1,320, re-run, and explain the effect.
- [ ] Restore the original values after experimenting.

### In your own words
**What did I change?**

_Write here._

**What happened to revenue growth and operating margin, and why?**

_Write here._

**What was confusing?**

_Write here._

## Next milestone

Learn how to read structured data from a file and automatically extract financial metrics. After that, connect real public filings while preserving their source and reporting periods.

No personal or confidential information should be committed to this public repository.

## FinSight research MVP — added 17 October 2026

The implementation now has a CSV/example workflow, validated observations, deterministic ratios, source tracking and exports. Live SEC access was verified and 48 KSPI/Apple/Microsoft figures were reconciled to standalone filing XBRL. See [walkthrough](docs/walkthrough.md) and [validation](docs/validation.md).

These are **your exercises**, not completed by the development assistant:

- [ ] Run the app and explain the synthetic-data label.
- [ ] Independently calculate the example's growth, margin and cash-flow proxy.
- [ ] Explain percentage change versus percentage-point change.
- [ ] Import the valid CSV and explain why the invalid example is rejected.
- [ ] Trace a calculated output's input IDs into the sources export.
- [ ] Write the negative-margin unit test described in the walkthrough.
- [ ] Explain why a mocked API test is not real-company reconciliation.
- [ ] When SEC access is available, trace one real observation to its filing.

**What did I personally run and change?**

_Write here._

**What does a passing test establish, and what does it not establish?**

_Write here._

- [ ] Analyse KSPI in KZT and explain the revenue-after-rewards definition.
- [ ] Explain why group income differs from parent-attributable income and why the simple cash-flow proxy is suppressed for KSPI.
