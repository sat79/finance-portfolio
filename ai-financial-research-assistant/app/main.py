"""Run with: python -m streamlit run app/main.py"""

from pathlib import Path

import pandas as pd
import streamlit as st

from finsight.csv_import import ImportError, import_csv
from finsight.examples import synthetic_example
from finsight.exports import csv_bundle, excel_bytes, tables
from finsight.financials import calculate, commentary
from finsight.models import LABELS, Metric
from finsight.research.ui import render_research
from finsight.sec import SUPPORTED, SECClient, SECError

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="FinSight | Financial research", page_icon="📊", layout="wide")
st.title("FinSight — Financial Research & Valuation Workspace")
st.caption(
    "Company research · cited evidence · deterministic financial analysis · optional model narrative"
)
st.write("Choose a source, review annual figures, check the evidence, then export your analysis.")
mode = st.radio(
    "Data source",
    ["Company research", "SEC company", "Upload CSV", "Synthetic example"],
    horizontal=True,
)
if mode == "Company research":
    render_research()
    st.stop()
ticker = (
    st.selectbox(
        "Supported company (search by ticker)",
        list(SUPPORTED),
        format_func=lambda t: f"{t} — {SUPPORTED[t][0]}",
    )
    if mode == "SEC company"
    else None
)
signature = (mode, ticker)
if st.session_state.get("source_signature") != signature:
    for key in ("dataset", "preview", "upload_digest", "upload_error"):
        st.session_state.pop(key, None)
    st.session_state.source_signature = signature

if mode == "SEC company":
    st.info(
        "Supported companies: Kaspi.kz (IFRS, KZT, 20-F), Apple and Microsoft (US GAAP, USD, 10-K). "
        "Set SEC_USER_AGENT in your shell to an app name and real contact email before fetching."
    )
    refresh = st.checkbox("Refresh official data (otherwise use a cache up to 24 hours old)")
    if st.button("Fetch SEC annual data", type="primary"):
        st.session_state.pop("dataset", None)
        try:
            with st.spinner("Retrieving official filings and selecting annual observations…"):
                st.session_state.dataset = SECClient().load(ticker, refresh=refresh)
        except (SECError, ValueError) as exc:
            st.error(str(exc))
            st.info(
                "You can choose Upload CSV or Synthetic example explicitly. Neither is live SEC data."
            )
elif mode == "Upload CSV":
    st.write(
        "Upload one company's annual facts in whole currency units. "
        "Files remain in this session's memory and are not sent to an external provider."
    )
    st.caption("UTF-8 CSV · maximum 1 MiB / 1,000 rows · schema version 1 · one currency")
    st.download_button(
        "Download fictional CSV template",
        (ROOT / "data/examples/valid_synthetic.csv").read_bytes(),
        "finsight-template.csv",
        "text/csv",
    )
    upload = st.file_uploader("Choose annual financial CSV", type=["csv"])
    financial_group = st.checkbox(
        "This CSV describes a banking or financial group (suppress simple FCF)"
    )
    if upload:
        import hashlib

        content = upload.getvalue()
        digest = (hashlib.sha256(content).hexdigest(), financial_group)
        if st.session_state.get("upload_digest") != digest:
            st.session_state.pop("dataset", None)
            st.session_state.pop("preview", None)
            st.session_state.pop("upload_error", None)
            st.session_state.upload_digest = digest
            try:
                st.session_state.preview = import_csv(content, financial_group=financial_group)
            except ImportError as exc:
                st.session_state.upload_error = str(exc)
        if st.session_state.get("upload_error"):
            st.error(st.session_state.upload_error)
        preview = st.session_state.get("preview")
        if preview:
            st.subheader("Import preview — user-provided, not SEC verified")
            st.dataframe(
                pd.DataFrame(
                    [
                        {k: str(v) if v is not None else "" for k, v in f.model_dump().items()}
                        for f in preview.selected
                    ]
                ),
                hide_index=True,
            )
            for warning in preview.warnings:
                st.warning(warning.message)
            if st.button("Analyse validated CSV", type="primary"):
                st.session_state.dataset = preview
    else:
        for key in ("dataset", "preview", "upload_digest", "upload_error"):
            st.session_state.pop(key, None)
else:
    st.warning(
        "FICTIONAL EXAMPLE — invented teaching numbers, no real company or SEC filing. "
        "This mode demonstrates the workflow; it does not validate real-company coverage."
    )
    if st.button("Load fictional example", type="primary"):
        st.session_state.dataset = synthetic_example(ROOT / "data/examples/valid_synthetic.csv")

if st.button("Clear session data"):
    for key in ("dataset", "preview", "upload_digest", "upload_error"):
        st.session_state.pop(key, None)

dataset = st.session_state.get("dataset")
if dataset is None:
    st.info("No analysis loaded. Choose a source and load data to begin.")
    st.stop()

st.header(dataset.company)
st.caption(
    f"CIK {dataset.cik} · source: {dataset.origin} · retrieved/imported (UTC): "
    f"{dataset.fetched_at.isoformat()}"
)
st.write(dataset.policy)
st.caption(
    f"Accounting basis: {dataset.accounting_basis} · amounts stay in their reported currency; no FX conversion"
)
if dataset.financial_group:
    st.warning(
        "Financial-group analysis: operating cash flow includes lending/deposit effects. "
        "The simple free-cash-flow proxy is not presented as distributable cash. "
        "Operating profit is not inferred from pretax profit."
    )
verified_kspi = dataset.cik == "0001985487" and dataset.origin in {"sec_live", "sec_cache"}
if verified_kspi:
    st.info(
        "KSPI revenue is consolidated IFRS revenue after customer rewards. Segment revenue before "
        "rewards is a different measure. FY2025 includes Hepsiburada and IAS 29 effects; reported "
        "growth is not organic growth. Group income and profit attributable to owners are shown separately."
    )
if dataset.origin == "synthetic_fixture":
    st.warning(
        "All figures below are fictional. No real-company reconciliation has been performed here."
    )
elif dataset.origin == "csv":
    st.warning("User-provided data. Source references have not been verified by FinSight.")
    if dataset.cik == "0001985487":
        st.warning(
            "This CSV identifies KSPI, but its revenue definition and accounting basis have not "
            "been verified. Confirm after-rewards revenue and group versus parent profit yourself."
        )
if len(dataset.periods) < 3:
    st.warning("Fewer than three annual periods available; multi-year analysis is limited.")

calculations = calculate(dataset)
export_tables = tables(dataset, calculations)
financials, ratios, sources, exports = st.tabs(
    ["Financial statements", "Ratios & trends", "Sources & warnings", "Export"]
)
lookup = {(f.end, f.metric): f for f in dataset.selected}
with financials:
    st.subheader("Reported or supplied financial figures")
    st.caption(
        "Whole currency units; original values retained. Missing means no supported unambiguous observation."
    )
    rows = []
    for metric in dataset.metrics:
        label = LABELS[metric]
        if verified_kspi and metric == Metric.REVENUE:
            label = "Consolidated IFRS revenue (after rewards)"
        elif dataset.financial_group and metric == Metric.NET_INCOME:
            label = "Group net income / loss (including non-controlling interests)"
        row = {"Metric": label}
        for period in dataset.periods:
            fact = lookup.get((period.end, metric))
            row[period.label] = (
                f"{fact.value:,.2f} {fact.currency}" if fact else "Missing — review warnings"
            )
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption(
        "Source/review limitations for the financial table (reported does not mean independently verified):"
    )
    st.dataframe(
        pd.DataFrame(
            [
                w.model_dump(mode="json")
                for w in dataset.warnings
                if w.code not in {"POLICY", "SCOPE"}
            ]
        ),
        hide_index=True,
    )
    st.caption(
        "Income and cash-flow metrics cover each fiscal interval. Cash, assets and liabilities are year-end balances."
    )
    chart = []
    for period in dataset.periods:
        row = {"Fiscal period": period.label}
        for metric in (Metric.REVENUE, Metric.OPERATING_PROFIT, Metric.OPERATING_CASH_FLOW):
            fact = lookup.get((period.end, metric))
            row[LABELS[metric]] = float(fact.value) / 1_000_000 if fact else None
        chart.append(row)
    currency = next(iter({f.currency for f in dataset.selected}), "reported currency")
    st.write(f"Financial trends ({currency} millions; rounded only for display)")
    st.line_chart(pd.DataFrame(chart).set_index("Fiscal period"))
with ratios:
    st.subheader("Calculated metrics")
    display = []
    for result in calculations:
        display.append(
            {
                "Period end": str(result.period_end),
                "Metric": result.metric,
                "Value": f"{result.value:,.2f}" if result.value is not None else "Missing",
                "Unit": result.unit,
                "Formula": result.formula,
                "Warning": result.warning or "",
                "Review limitations": "; ".join(result.review_warnings),
            }
        )
    st.dataframe(pd.DataFrame(display), hide_index=True, width="stretch")
    trend = [
        {
            "Period end": str(p.end),
            **{
                c.metric: float(c.value) if c.value is not None else None
                for c in calculations
                if c.period_end == p.end and c.unit == "percent"
            },
        }
        for p in dataset.periods
    ]
    st.write("Ratios and growth (%) — fiscal period ends")
    st.line_chart(pd.DataFrame(trend).set_index("Period end"))
    st.info(
        "Revenue growth compares consecutive compatible fiscal years. Margins divide profit by revenue. "
        "Margin changes are percentage points. The cash-flow proxy is operating cash flow less purchases "
        "of property, plant and equipment (positive outflow). It is not a full FCFF valuation input."
    )
    st.subheader("Rule-based observations")
    for line in commentary(dataset, calculations):
        st.write(line)
    st.caption(
        "Derived from the calculations above. No causal explanations or generative AI are used."
    )
with sources:
    st.subheader("Trace each observation")
    source_rows = [
        {k: str(v) if v is not None else "" for k, v in row.items()}
        for row in export_tables["sources"]
    ]
    st.dataframe(
        pd.DataFrame(source_rows),
        hide_index=True,
        width="stretch",
        column_config={"source_url": st.column_config.LinkColumn("SEC filing index")},
    )
    st.write(
        "fact_id identifies an observation. Calculated metrics export their input_ids. "
        "Unselected competing observations remain in this table and in exports."
    )
    for url in sorted({f.source_url for f in dataset.selected if f.source_url}):
        st.link_button("Open SEC filing index", url)
    st.subheader("Warnings and missing data")
    st.dataframe(
        pd.DataFrame(
            [
                {k: str(v) if v is not None else "" for k, v in row.items()}
                for row in export_tables["warnings"]
            ]
        ),
        hide_index=True,
    )
    st.caption(
        "Latest available disclosures may incorporate revisions. Accounting comparability still needs analyst review. "
        "No historical point-in-time claim is made."
    )
with exports:
    st.write(
        "Export financials, calculations, all source observations, warnings, and analysis metadata."
    )
    st.download_button(
        "Download CSV bundle",
        csv_bundle(dataset, calculations),
        "finsight-analysis.zip",
        "application/zip",
    )
    st.download_button(
        "Download Excel workbook",
        excel_bytes(dataset, calculations),
        "finsight-analysis.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.caption(
        "Excel amounts are numbers when they fit its 15-significant-digit precision; larger-precision amounts "
        "remain text. Percentages are numeric and rounded to 15 significant digits. exact_value preserves "
        "every Decimal as text; value_storage explains the choice. CSV preserves exact decimal text. "
        "Identifiers stay text, and formula-like source text is escaped."
    )
