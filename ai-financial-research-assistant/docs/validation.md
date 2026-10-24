# Validation evidence — 17 October 2026

Environment: Linux x86_64, Python 3.12.14, project-local virtual environment and pinned `requirements-lock.txt`. This is evidence for the scoped research MVP, not universal financial-data accuracy or deployment.

## Executed checks

| Command / check | Actual result |
|---|---|
| `python -m pip install -r requirements.txt` | Installed successfully; repeated installation succeeded |
| `python -m pip check` | No broken requirements |
| `python -m pytest -q` | **102 passed**, zero failures/skips (unit, schema, parser, mocked transport, exports and Streamlit AppTest); original 80-test baseline reproduced before changes |
| `ruff check .` / `ruff format --check .` | Passed |
| Root `python scripts/check_portfolio.py` (prior milestone) | Passed existing structure/checksum, 42 portable unit tests, workbook checks and KSPI reference analysis; unrelated projects were not changed or retested in this scoped continuation |
| `python scripts/validate_live.py --output /workspace/finance-validation/finsight-live` | Actual SEC retrieval passed for KSPI (three periods), AAPL and MSFT (five periods each); sample reconciliation performed separately below |
| `python scripts/reconcile_xbrl.py --filings /workspace/finance-validation --output /workspace/finance-validation/finsight-reconciliation-rechecked.csv` | **48/48 selected observations match** separately downloaded official XBRL instances; zero differences |
| Streamlit HTTP `/_stcore/health` | `ok` |
| Chromium browser, offline/CSV | Example loaded; hand-checked ratios displayed; CSV/XLSX download completed; invalid capex rejected; valid CSV preview/analysis and source inspection passed; source change cleared previous results; missing SEC configuration shown explicitly |
| Chromium browser, actual SEC/cache | All three companies loaded; ratios and filing links visible; CSV and XLSX downloads succeeded; 15 AAPL, 15 MSFT and 18 KSPI amounts matched the independent sample in both formats. XLSX cells were numeric, exact backups/CIKs preserved, and no formula cells present |
| Intel Mac wheel availability | `pip download --only-binary=:all: --platform macosx_12_0_x86_64 --python-version 312 --implementation cp --abi cp312 --dest /tmp/finsight-macos12-wheels -r requirements-lock.txt` passed; same check for `macosx_14_0_x86_64` passed. This does not execute the packages on macOS |
| Local launcher | `bash -n scripts/start.sh`, help/no-identification path, invalid-identification rejection and both live/offline Streamlit launches passed on Linux |

The first live attempts received proxy HTTP 403/CONNECT denial. After network settings became available, identified requests succeeded. The final evidence above reflects successful requests, not an assumption that saving a configuration draft applied it. One browser check initially queried filing links before rendering completed; waiting for the element resolved the test synchronization failure. After extending the Pydantic schema for KSPI, a running Streamlit process retained old module classes and raised an attribute error; restarting that owned process loaded the new schema and the full browser check passed. Restart Streamlit after schema/dependency changes. No financial assertions were relaxed.

## Real-company evidence

| Company | Periods independently checked | Values checked | Official filing |
|---|---|---|---|
| Apple | FY2023, FY2024, FY2025 (September year-ends; FY2023 53 weeks) | Revenue, operating profit, net income, CFO, purchases of PP&E | [2025 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm), accession 0000320193-25-000079 |
| Microsoft | FY2024, FY2025, FY2026 (June year-ends) | Same five metrics | [2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm), accession 0001193125-26-323660 |
| Kaspi.kz | FY2023, FY2024, FY2025 (December year-ends) | Revenue, group profit, parent-attributable profit, pretax profit, CFO, property/equipment/intangible purchases | [2025 20-F](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/kspi-20251231.htm), accession 0001985487-26-000008 |

`docs/reconciliation.csv` records each amount, period, independent XBRL amount, difference, context ID, accession, source URL and SHA-256. Independent here means a separate read of the **filed XBRL instance**, filtering consolidated duration contexts and the reported USD/KZT units without calling the application selector. This is not a third-party audit. The rendered statement rows were also inspected: reported tables use millions; the app keeps whole USD/KZT. PP&E purchases appear as parenthesised outflows in cash-flow statements, while the XBRL Payments concept and app use a positive outflow before subtraction. No discrepancies were found in the 48-value sample.

Illustrative arithmetic checks (currency as stated):

- Apple FY2025 (USD millions): CFO 111,482 − PP&E purchases 12,715 = **98,767** cash-flow proxy; operating margin 133,050 / 416,161 = **31.9708%**.
- Microsoft FY2026 (USD millions): CFO 182,935 − PP&E purchases 115,948 = **66,987** cash-flow proxy; operating margin 155,237 / 331,839 = **46.7808%**.
- KSPI FY2025 (KZT millions): consolidated revenue 4,046,074 = segment revenue 4,101,961 − customer rewards 55,887. Group net margin 1,067,707 / 4,046,074 = **26.3887%**. Its simple FCF proxy is deliberately suppressed; see [KSPI methodology](kspi-methodology.md).

Frozen numerical records and explicit expected values are in `tests/fixtures/reconciled_companies.json`; they are dated historical evidence, **not live data**. Full filings and entire API datasets are kept outside the checkout during validation and are not committed. Cash/assets/liabilities and earlier displayed years retain provenance but are not part of this independent 48-value sample.

## Reproduce the independent source check

The live script always generates a new outcome and leaves manual reconciliation marked pending; it does not inherit this historical sample's validation. To reproduce the frozen sample, download the three `filing_xml_url` documents specified in `tests/fixtures/reconciled_companies.json` using your identifying SEC User-Agent and respectful request spacing. Save them as `AAPL-instance.xml`, `MSFT-instance.xml` and `KSPI-instance.xml` in a local directory, then run:

```bash
python scripts/reconcile_xbrl.py --filings /path/to/filings --output exports/reconciliation.csv
```

The checker requires the original reviewed source hashes, independently extracts matching annual consolidated reported-currency contexts, and fails on missing, ambiguous or differing values. To validate a newer filing, make a new explicitly reviewed snapshot instead of relabelling this old result.

## Browser checks

Playwright/Chromium are optional validation tools, not app dependencies. In the development machine, preinstalled Playwright and `/usr/bin/chromium` were used. Elsewhere, install Playwright in a separate test environment and supply a Chromium binary path using `FINSIGHT_CHROMIUM`. No automated browser installation or paid service is required by the app.

With an app started **without** SEC_USER_AGENT on port 8501, run `python scripts/browser_smoke.py` for offline/CSV/config-error flows. With identification configured and the app on port 8502, run `python scripts/browser_live_smoke.py`. `FINSIGHT_BASE_URL` overrides the local test URL. The live browser check compares exported values with the frozen historical reconciliation sample, so future revisions require investigation. These scripts are not part of CI because they require an installed browser and, for live testing, a valid contact identity/network access.

## User-task coverage

| User task | Observed outcome | Limitation |
|---|---|---|
| Select company, review performance | KSPI/AAPL/MSFT → fetch → three/five/five annual periods | Only documented companies/standard concepts |
| Identify historical changes | Tables/charts and deterministic growth/margins/cash proxy rendered | No causal explanation or investment recommendation |
| Trace a figure | Filing links, concept/date/accession records and exported input IDs inspected | Source review still needs analyst judgment |
| Export to Excel | Browser downloads/read-back passed; numeric `value` cells and exact text backups verified for all 48 sampled amounts, plus precision-boundary, missing, negative, identifier and injection tests | Native desktop Excel open/recalculation and user acceptance not executed |
| Understand missing/invalid data | Missing denominators, incompatible units, conflicting disclosures and invalid CSV cases tested | Not every real accounting ambiguity is detectable |

No user time-saving claim is made: task durations and a manual-work baseline were not measured. No Mac, Windows, Colab, mobile, production deployment, concurrent multi-process rate-limit or desktop Excel recalculation test was performed. These remain explicit limits, not hidden acceptance failures for the local scoped MVP.

## Continuation quality-review evidence

The [quality review](quality-review.md) records severity and decisions. Before fixing the reproduced problems, the expanded targeted suite had **13 failing regressions** for text-only numbers, XML-invalid CSV characters and misleading KSPI CSV labelling. All now pass. The total grew from 80 to 102 with precision-boundary, injection and three-company workbook coverage. No accounting calculation or source-selection policy was loosened.

Fresh requests on 17 October 2026 were made using `python scripts/validate_live.py --output /workspace/finance-validation/finsight-review-live`: KSPI three periods, AAPL/MSFT five each, all successful. As designed, that script leaves independent reconciliation pending. Separately, `python scripts/reconcile_xbrl.py --filings /workspace/finance-validation --output /workspace/finance-validation/finsight-review-reconciliation.csv` reproduced all **48/48** frozen source matches. Browser exports from the freshly populated cache matched the same historical values in CSV and numeric XLSX. Rendered statement text was spot-checked for the documented Apple, Microsoft and KSPI examples, including units, purchase signs and KSPI group/parent profit. The frozen checker alone is not a comparison of every current app observation.

The updated browser commands were `FINSIGHT_BASE_URL=http://127.0.0.1:8503 python scripts/browser_smoke.py` (no SEC identification) and `FINSIGHT_BASE_URL=http://127.0.0.1:8504 python scripts/browser_live_smoke.py` (identified requests/cache). Both passed using system Playwright/Chromium. Workbook inspection used openpyxl; no desktop Excel engine was used.

Visual inspection covered the rendered KSPI table and its prominent accounting warnings at 1440px width. The live smoke script now opens Financial statements for each company before waiting for both the financial grid and actual chart rendering. Initial inspection probes timed out because one expected a canvas instead of Streamlit's SVG, and another left the Export tab selected between companies. The corrected checks inspect the visible tab and accept SVG/canvas rendering; no financial assertions changed. Mobile/responsive acceptance was not performed.

Evidence types remain distinct: **unit/regression tests** check arithmetic/schema/boundaries; **mocked integration and AppTest** check pipeline/UI handling; **browser tests** check actual downloads/navigation; **fresh SEC retrieval** checks live access; **real-data reconciliation** checks the limited historical source sample. **Manual user acceptance on Mac/Chrome/Excel is pending**, with no boxes checked on the user's behalf. No dependency vulnerability scan or benchmark/load test was performed.
