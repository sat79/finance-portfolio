## New company research acceptance

Follow [Research a company](research-guide.md) for Kaspi.kz, Microsoft and Apple. Confirm Apple’s legal entity explicitly, review document/news coverage and download each report bundle. Try NVIDIA to check the unsupported financial-coverage message, and a private/nonexistent company to check no-match handling. Inspect citation URLs, fiscal periods, warnings and KSPI’s suppressed FCF proxy. Record your Mac/browser/Excel result; cloud replay does not complete local acceptance.

# Your three-company acceptance test

**Status: not performed by the user. All boxes intentionally unchecked.** The developer's Linux browser checks do not complete your Mac/Chrome/Excel acceptance. Follow [Mac setup](mac-setup.md) first. Record your date, macOS/Python/Excel versions and any failure in your own notes.

These expected figures describe historical filings reviewed on **17 October 2026**. Future live data can contain revisions; investigate a mismatch through accession and period rather than forcing a pass. App amounts are **whole currency units**, while these filings display **millions**. Do not confuse a fiscal year with a calendar year.

## Apple: verify a figure and calculate a ratio

- [ ] Select **SEC company → AAPL → Fetch SEC annual data**. Confirm Apple Inc., CIK `0000320193`, USD and US GAAP.
- [ ] Find **FY2025 (2025-09-27)** in Financial statements. Revenue should be **416,161,000,000 USD** and operating profit **133,050,000,000 USD** for this historical snapshot. The interval is 2024-09-29 to 2025-09-27.
- [ ] Open **Sources & warnings**. Find selected `revenue`, ending 2025-09-27, concept `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`. Inspect filing accession, date, `fact_id` and `selected=True`. Open the filing index and choose the annual report. The reviewed [2025 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) is accession **0000320193-25-000079**.
- [ ] In that report, find **Consolidated Statements of Operations** (printed page 29): “Total net sales” **416,161** and “Operating income” **133,050**, in USD millions. Multiply each by 1,000,000 to compare with the app. Record the actual source you checked.
- [ ] Calculate `133050 / 416161 * 100` using a calculator. Expect **31.9708%**, displayed as **31.97%** operating margin. This is a ratio, not revenue growth. Margin movements between years are percentage points.
- [ ] Optionally verify cash-flow proxy: CFO **111,482** less PP&E purchases **12,715** = **98,767 USD million**. Purchases are positive outflows for subtraction even though the statement shows parentheses. This proxy is not full FCFF.

## Excel: confirm numbers work as numbers

- [ ] Download the workbook from **Export**, open it in your desktop Excel and confirm sheets `financials`, `calculations`, `sources`, `warnings`, `metadata`. It should open without a repair message or macros. Do not enable external content.
- [ ] In `financials`, filter `fiscal_year` to 2025 and `metric` to `revenue`, then `operating_profit`. Copy the two **value** cells to a new sheet, revenue into A1 and operating profit into A2. `=ISNUMBER(A1)` and `=ISNUMBER(A2)` should both return TRUE.
- [ ] Enter `=A2/A1` and apply Excel Percentage format with four decimal places. Expect **31.9708%**. This checks arithmetic on the downloaded numeric cells, not just a typed example.
- [ ] In `calculations`, the corresponding `operating_margin` value is stored as approximately **31.9707997625919**, with a literal percent-sign display. It already represents percent: do **not** apply Excel's ordinary Percentage format again or it will display roughly 3197%. Divide by 100 first if you need an Excel fractional percentage.
- [ ] Check `exact_value` retains the full Decimal text, `original_value` retains source text, and `value_storage` explains number/text/rounding. CIK `0000320193` must retain its leading zeros; accessions and observation IDs must stay text. Amounts exceeding 15 significant digits intentionally remain text; ordinary sampled company amounts are numeric.
- [ ] Match a calculation's `input_ids` to `fact_id` entries in `sources`. A missing calculation stays blank with an explanation; it must not turn into zero.

## Microsoft: repeat a shorter check

- [ ] Select MSFT and fetch. Confirm Microsoft Corporation, CIK `0000789019`, US GAAP/USD, and the June fiscal year-end.
- [ ] For **FY2026 (2026-06-30)**, compare revenue **331,839,000,000 USD** and operating profit **155,237,000,000 USD** with the [2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm), accession **0001193125-26-323660**. Search “Income Statements”; the corresponding figures are 331,839 and 155,237 in USD millions.
- [ ] Calculate `155237 / 331839 * 100` = **46.7808%**, displayed **46.78%**. Export and confirm numeric `value` cells as for Apple. Do not treat Microsoft FY2026 as the same dates as Apple FY2025.

## KSPI: examine the accounting differences

- [ ] Select KSPI and fetch. Confirm Joint Stock Company Kaspi.kz, CIK `0001985487`, IFRS, KZT and 20-F. Read the prominent financial-group and scope-change messages.
- [ ] For **FY2025 (2025-12-31)**, compare consolidated revenue **4,046,074,000,000 KZT** with **4,046,074 KZT million** in the [2025 20-F](https://www.sec.gov/Archives/edgar/data/1985487/000198548726000008/kspi-20251231.htm), accession **0001985487-26-000008**. It is after customer rewards: segment revenue 4,101,961 − rewards 55,887 = 4,046,074 million. See [KSPI methodology](kspi-methodology.md).
- [ ] Distinguish group net income **1,067,707** from parent-attributable income **1,073,177**, both KZT million. Non-controlling interests have a **5,470 million loss**, so parent profit can exceed group profit. Group net margin is `1067707 / 4046074 * 100` = **26.3887%**.
- [ ] Confirm operating profit is not replaced by pretax profit, broad investment purchases are not labelled PP&E-only capex, and the simple FCF proxy is unavailable with an explanation. Export and confirm missing FCF stays blank.
- [ ] Explain why lending, deposits and regulatory capital prevent interpreting group CFO as distributable cash. Explain why FY2025 reported revenue growth, including Hepsiburada and IAS 29 effects, is not organic growth.

## Record your result

| Check | Your result (leave blank until performed) | Evidence or issue |
|---|---|---|
| Mac installation and Chrome launch | | |
| Apple source and manual ratio | | |
| Desktop Excel numeric arithmetic and identifiers | | |
| Microsoft fiscal period and ratio | | |
| KSPI definitions and suppressed FCF | | |

Keep source references, expected/observed values and exact errors. A mismatch is a review item, not a reason to tick the box anyway. Your learning exercises in `LEARNING_LOG.md` remain unchecked.
