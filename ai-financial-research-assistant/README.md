# FinSight — Financial Research & Valuation Workspace

A Python/Streamlit research MVP for reviewing annual financial figures, deterministic ratios, provenance and analyst exports. The working product name is **FinSight AI**; this milestone contains no LLM or valuation engine.

**Status:** scoped Phase 1 research MVP. Live SEC retrieval returned three annual periods for **Kaspi.kz (KSPI)** and five each for **Apple (AAPL)** and **Microsoft (MSFT)**; **48 sampled figures** across three periods per company matched the standalone filing XBRL. Offline/CSV tests remain distinct from this live evidence. See [validation evidence](docs/validation.md) for the exact scope and limitations.

## What works

- Strict annual CSV import with preview, missing-data states and understandable errors.
- An explicitly fictional three-year example, including a loss and negative cash flow.
- Revenue growth, operating/net margins and operating cash flow less PP&E purchases; input provenance, warnings and rule-based observations.
- Financial tables/charts, source-observation review, CSV ZIP and Excel exports.
- A SEC connector for KSPI/AAPL/MSFT with official ticker-to-CIK verification, company-specific 10-K/20-F selection, retained competing disclosures, timeouts, retries, rate limits and dated caching. Its transport and selection have synthetic edge-case tests and live KSPI/Apple/Microsoft validation. Coverage remains limited to the documented companies and concepts.

No paid API, database or credentials are needed for the CSV/example workflow. The SEC connector requires a real identifying contact email in local configuration, not an API key.

## Install (Python 3.12)

**First time on an Intel Mac?** Follow the [step-by-step Mac setup](docs/mac-setup.md), then the [Apple → Microsoft → KSPI acceptance checklist](docs/acceptance-test.md). Native macOS and desktop Excel execution remain untested here; the guide distinguishes those checks from Linux validation.

From the repository root:

```bash
cd ai-financial-research-assistant
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

Use `python3` if it is already Python 3.12. A separate environment avoids conflicts with the other portfolio projects. The tested full lock is `requirements-lock.txt`; direct version constraints live in `pyproject.toml`. Linux/Python 3.12.14 was tested. On an Intel Mac, install Python 3.12 from python.org if needed, then use the same Terminal commands. macOS installation has not been executed here.

## Run

```bash
python -m streamlit run app/main.py
```

Or run `bash scripts/start.sh`: it uses the project environment, prompts for SEC contact identification when needed, and binds the server to your own computer. It does not install dependencies, save the email, or automatically execute `.env`.

Open the local address printed by Streamlit on your own machine. Select **Synthetic example → Load fictional example** for the fully offline walkthrough, or **Upload CSV** to supply your own data. Navigate **Financial statements → Ratios & trends → Sources & warnings → Export**. Both example CSVs are in `data/examples/`. CSV uploads are user-provided, never SEC-verified.

For live SEC requests, set identification in your shell before starting the app:

```bash
export SEC_USER_AGENT='FinSightAI your-real-contact-email'
```

Replace the placeholder with your real contact email; do not commit it. You can keep the export command in an ignored `.env` file and run `source .env`. The app intentionally does not automatically execute `.env` files. SEC access needs HTTPS to `www.sec.gov` and `data.sec.gov`. Select **SEC company**, choose KSPI (default), Apple or Microsoft, and click **Fetch SEC annual data**. An access failure is displayed without substituting example data.

The local cache defaults to `.cache/sec`; optionally set `FINSIGHT_CACHE_DIR` to another writable directory. **Clear session data** removes loaded data from the UI. It does not delete the public SEC disk cache. See [data handling and limitations](docs/limitations.md).

## Verify

```bash
python -m pytest -q
ruff check .
ruff format --check .
python scripts/validate_live.py --output exports/live-validation
```

The first three commands work offline after installation. The live script requires SEC identification and network access; exits nonzero when retrieval fails, writes the actual outcome, and does **not** mark independent reconciliation complete. An optional real-browser check is documented in [validation.md](docs/validation.md).

To trace a figure, open **Sources & warnings**, find its metric and period, and follow the SEC filing-index link when available. Confirm the financial statement's definition, fiscal dates and units. For a CSV, inspect the supplied reference yourself. Calculated outputs carry `input_ids` pointing to source `fact_id`s in the export. The synthetic example has no real filing links.

## Learn and inspect

- [Beginner walkthrough and one exercise](docs/walkthrough.md)
- [Intel Mac setup](docs/mac-setup.md) and [your acceptance checklist](docs/acceptance-test.md)
- [Phase 1 quality review and fixes](docs/quality-review.md)
- [Ranked Phase 2 proposal — awaiting approval](docs/phase-2-proposal.md)
- [Architecture/audit and ordered backlog](docs/audit-and-plan.md)
- [Financial methodology and annual selection](docs/methodology.md)
- [KSPI reporting definitions and financial-group controls](docs/kspi-methodology.md)
- [Data dictionary and CSV schema](docs/data_dictionary.md)
- [Validation results and remaining checks](docs/validation.md)
- [Limitations and costs](docs/limitations.md)
- [Changelog](CHANGELOG.md)

The original [Lesson 01 notebook](01_financial_metrics.ipynb) and [learning log](LEARNING_LOG.md) are retained. The notebook remains a standalone Colab introduction with fictional values. For learning in Colab, clone the repository, install this project and run the pure Python functions/tests; an interactive Streamlit deployment or public tunnel is not part of these instructions.

## Scope and financial interpretation

SEC scope: KSPI (IFRS, KZT, 20-F), Apple and Microsoft (US GAAP, USD, 10-K), with recent annual filings and explicit standard tags. The policy selects latest available compatible observations, retains competitors and flags uncertainty; it is not historical point-in-time reconstruction. For Apple/Microsoft, the free-cash-flow proxy is **CFO less purchases of PP&E**, not complete FCFF. For KSPI it is suppressed: bank cash flows are not distributable cash. KSPI revenue is after customer rewards; group/parent profit and broader investment purchases remain separate. See [KSPI methodology](docs/kspi-methodology.md). Losses are valid, missing figures are never zero-filled, and no business causes are invented.

AI research, documents, valuation, hosting and deployment remain future milestones. No service was deployed, no paid resources were created and no licence was added. Review current SEC terms before public hosting or redistributing real-company data.
