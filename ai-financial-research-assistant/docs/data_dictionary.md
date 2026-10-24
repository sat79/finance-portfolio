# Data dictionary and CSV schema

Source observations (`Fact`) and calculated outputs (`Calculation`) are separate records. `Dataset` retains every accepted observation and identifies which ones were selected.

| Field | Meaning |
|---|---|
| company / cik | Entity name and ten-digit SEC identifier; CSV identifiers are user assertions |
| metric / concept | Normalised metric and original XBRL tag; `manual:...` for CSV |
| value / original_value | Decimal amount and original numeric text; never scaled/replaced |
| currency / unit | Three-letter currency and whole currency units; SEC profiles use USD for AAPL/MSFT and KZT for KSPI |
| start / end / kind | Exact duration interval or instant balance date |
| fiscal_year | Year assigned from the period's own annual filing, or CSV assertion |
| source_fiscal_year / fiscal_period | Original filing FY and FY designation; a comparative fact may refer to an earlier period |
| form / filed / accession | Original filing identity; CSV uses form CSV and has no verified filing |
| source_url / source_id | SEC filing-index URL and CompanyFacts concept endpoint; CSV has a hash/row/reference identifier and no verified URL |
| status | reported, user_provided or synthetic; derived records separately say calculated |
| fact_id | Deterministic hash of the full observation; calculation input_ids point here |
| warnings | Observation warnings; dataset-level warnings include period and metric where applicable |
| fetched_at / origin | UTC time and sec_live, sec_cache, csv or synthetic_fixture; cached time is oldest component retrieval |
| source_hashes | Hashes of retrieved source payloads or uploaded bytes for reproducibility; not proof of authenticity |

## CSV version 1

Exact UTF-8 header (order matters):

```csv
schema_version,company,cik,fiscal_year,period_start,period_end,currency,unit,metric,value,source_reference
```

One company, one currency, one metric per annual period. Select the financial-group checkbox when appropriate; the known KSPI CIK also enables this control automatically. Financial-group imports suppress the simple FCF proxy. Allowed metrics: `revenue`, `operating_profit`, `net_income`, `operating_cash_flow`, `capex`, `cash`, `assets`, `liabilities`; optional explicit `parent_net_income`, `pretax_profit`, `investment_purchases`. Supply the fiscal interval on all rows; instant metrics are stored at the interval end. Use strict `YYYY-MM-DD` dates and a four-digit fiscal year. Supported annual lengths are 350–380 days. Overlapping intervals and conflicting FY labels are rejected.

Use `schema_version=1`, a ten-digit CIK (including leading zeros), and whole currency units such as `USD,USD`. Convert thousands/millions explicitly before importing and describe that transformation in `source_reference`. No automatic unit or FX conversion. A blank value means missing; negative profit and cash flow are permitted. Values must be plain decimals: no grouping commas, currency symbols, exponents, formulas, infinity or NaN. A positive capex value means an outflow. Provide a meaningful human-readable source reference; it is not treated as verified or fetched as a URL.

Maximum upload: 1 MiB, 1,000 rows, 500 characters per field. Required dates, names and references cannot be blank. Duplicate records are rejected even if their values agree. One row cannot overwrite another. Files are parsed/validated and previewed before analysis; no uploaded code is executed.

`data/examples/valid_synthetic.csv` has three fictional June year-ends and includes a loss and negative CFO. `invalid_negative_capex.csv` demonstrates rejection. Neither file is real-company evidence.

`accounting_basis`, `financial_group` and the supported metric list are retained in the dataset; exports include accounting basis and financial-group status. CSV accounting basis remains user-provided.

## Exports

CSV ZIP and XLSX contain `financials`, `calculations`, `sources` (including unselected observations), `warnings` and `metadata`. CSV retains exact decimal text. XLSX `value` cells are numbers for amounts with at most 15 significant digits; amounts requiring greater precision stay exact text. Percentage calculations are rounded to 15 significant digits and remain numeric. Blank calculations remain blank, never zero.

XLSX additionally includes `exact_value` (the full Decimal string) and `value_storage` (`number`, rounded number, exact text, or missing) on financials/calculations/sources. `original_value` remains the original source numeric text. Numeric amounts are in whole currency units, not millions. Percentage values already represent percentages (31.97 means 31.97%); Excel uses a literal percent-sign format without multiplying by 100. Divide by 100 before applying Excel's standard Percentage format if a fractional percentage is needed.

Identifiers, including CIK/accession/fact IDs, remain text, preserving leading zeros. Formula-like **text** is prefixed with an apostrophe; validated negative numerical values remain negative. Unsupported control/XML characters are rejected on CSV import. Input IDs link calculations to source observations. User-provided source references are text, never invented SEC citations. Actual desktop Excel recalculation remains an acceptance check; exported numeric cells were checked by reading the generated XLSX.
