# AI Financial Research Assistant — Learning Project

**Status: Phase 1 — Python and financial reasoning (not yet an AI application)**

A practical project for learning how to build trustworthy AI tools for financial research. The long-term goal is to read public company reports, extract financial figures, calculate and check ratios, and generate source-backed analysis.

This project starts with **deterministic Python calculations**, because financial numbers should not be invented or calculated solely by a language model.

## Start here (no installation needed)

1. Open [Lesson 01 in Google Colab](https://colab.research.google.com/github/sat79/finance-portfolio/blob/main/ai-financial-research-assistant/01_financial_metrics.ipynb).
2. Click **Connect** if Colab asks for a runtime.
3. From the **Runtime** menu, select **Run all**.
4. Read the output, then do the exercise near the bottom: change the example 2024 revenue and re-run the calculations.
5. Write what you learned in [LEARNING_LOG.md](LEARNING_LOG.md).

**Expected example output:**
- Revenue growth, 2023–2024: **13.64%**
- Operating margin 2023: **12.73%**
- Operating margin 2024: **14.00%**
- Margin improvement: **1.27 percentage points**

The company and numbers in this lesson are **fictional, for teaching purposes**. They are not investment research or investment advice.

## Roadmap

| Phase | Skill | Proof of work |
|---|---|---|
| 1 | AI basics, Python, ratio calculations | Reproducible notebook and learning log |
| 2 | APIs, public filings, data validation | Traceable financial data extraction |
| 3 | LLM APIs and retrieval (RAG) | Answers with document-level citations |
| 4 | Evaluation, security, costs and deployment | Test results and live demonstration |
| 5 | Career presentation and certification | Project demo, write-up and targeted CV evidence |

## Engineering principles

- Always distinguish **reported figures, derived calculations, and AI-generated commentary**.
- Show source location, reporting year, units and accounting context for real figures.
- Verify arithmetic in code, not by asking a model to guess the answer.
- Use public data or explicitly synthetic examples; do not commit secrets or private information.
- State limitations and failures clearly.

## Tools and cost

- **Python 3 in Google Colab:** can be used without local installation.
- **GitHub:** source control and documentation.
- No API keys, paid subscriptions, or external packages are needed for Lesson 01.

This is a learning-stage project, and further functionality will be added as it is built and tested.
