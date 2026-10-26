"""One visible company-to-report journey; financial-only workflows remain available."""

import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from finsight.research.identity import find_companies
from finsight.research.model_evidence import build_model_evidence, fact_text
from finsight.research.narrative import ModelConfig, OpenAIProvider, api_key, estimate
from finsight.research.outcomes import assess
from finsight.research.report import build_report, manual_synthesis_bundle, report_bundle
from finsight.research.workflow import run_research
from finsight.sec import SECClient, SECError


def render_research():
    st.subheader("Research a company")
    st.write(
        "Enter a company name or ticker, confirm the entity, then build a cited research report from official filings, financial data and recent news."
    )
    st.caption(
        "SEC name search covers its US-listed directory. Reviewed financial extraction covers KSPI, Apple and Microsoft; identifying another company does not extend accounting coverage."
    )
    with st.form("company_search"):
        query = st.text_input(
            "Company name or ticker", placeholder="Apple, Microsoft, Kaspi.kz, or a ticker"
        )
        submitted = st.form_submit_button("Find company")
    if submitted:
        st.session_state.pop("research_result", None)
        st.session_state.pop("research_narrative", None)
        st.session_state.pop("company_matches", None)
        try:
            with st.spinner("Searching the official SEC directory…"):
                matches = find_companies(SECClient(), query)
            st.session_state.company_matches = matches[:10]
            if len(matches) > 10:
                st.warning(
                    f"{len(matches)} listings match; showing 10. Narrow the name if your company is not shown."
                )
            if not matches:
                st.warning(
                    "No matching US-listed entity found in the SEC directory. Private companies, non-US-only listings and alternate names may be outside this directory. No company was substituted."
                )
        except (SECError, ValueError) as exc:
            st.error(str(exc))
    matches = st.session_state.get("company_matches", [])
    if not matches:
        st.info(
            "Start with a name search. Configure SEC_USER_AGENT locally to retrieve official evidence."
        )
        return
    if len(matches) > 1:
        st.info(
            "Several listings match. Choose the intended legal entity; the app will research only your selection."
        )
    company = st.selectbox(
        "Confirm company",
        matches,
        index=None if len(matches) > 1 else 0,
        format_func=lambda c: f"{c.name} | {c.ticker} | {c.exchange} | CIK {c.cik}",
    )
    if company is None:
        st.info("Select a legal entity before starting research.")
        return
    previous = st.session_state.get("research_result")
    if previous and previous.company.cik != company.cik:
        st.session_state.pop("research_result", None)
        st.session_state.pop("research_narrative", None)
    st.caption(
        "Financial extraction: "
        + (
            "reviewed profile available"
            if company.supported
            else "unsupported — a document report will explain the financial coverage gap"
        )
    )
    today = datetime.now(timezone.utc).date()
    left, right = st.columns(2)
    start = left.date_input("News from", today - timedelta(days=89), max_value=today)
    end = right.date_input("News through", today, max_value=today)
    refresh = st.checkbox("Refresh evidence from sources (otherwise reuse dated cache)")
    if st.button("Research selected company", type="primary"):
        st.session_state.pop("research_narrative", None)
        with st.status("Building company research…", expanded=True) as status:

            def progress(stage, result):
                st.session_state.research_result = result
                st.write(f"{stage}: {result.stages[stage]}")

            try:
                result = run_research(company, start, end, refresh=refresh, progress=progress)
                st.session_state.research_result = result
                build_report(result)
                coverage = assess(result)
                result.stages["Analysis"] = coverage["status"] + ": deterministic report rendered"
                status.update(
                    label=f"Research {coverage['status']} — review evidence coverage",
                    state="complete" if coverage["status"] == "complete" else "error",
                    expanded=coverage["status"] != "complete",
                )
            except (SECError, ValueError, OSError) as exc:
                status.update(
                    label="Research interrupted — completed evidence retained", state="error"
                )
                st.error(str(exc))
    result = st.session_state.get("research_result")
    if not result:
        return
    if result.news_start != start or result.news_end != end:
        st.info(
            "The report below retains its original company/date settings. Click Research selected company to apply your changed selection."
        )
    coverage = assess(result)
    st.header(f"Research report: {result.company.name}")
    message = f"Research {coverage['status']}: " + (
        "; ".join(coverage["missing"]) or coverage["scope"]
    )
    if coverage["status"] == "failed":
        st.error(message)
    elif coverage["status"] == "partial":
        st.warning(message)
    else:
        st.success(message)
    st.write(
        f"Official documents: **{coverage['official_documents']['status']}** · "
        f"Annual financial extraction: **{coverage['financial']['status']}** · "
        f"Independent news: **{coverage['independent_news']['label']}**"
    )
    st.write("**Table analytical evidence:** " + coverage["tables"]["summary"])
    st.caption(coverage["tables"]["scope"])
    st.caption(
        f"Cut-off {result.cutoff.isoformat()} · measured retrieval/extraction time {result.seconds.get('total', 0):.1f}s · deterministic report: 0 model calls, $0 model cost. Optional narrative usage is shown separately below."
    )
    if result.limitations:
        st.warning(
            f"{len(result.limitations)} coverage limitations apply. Review missing documents, "
            "news access and financial coverage before using this report."
        )
        with st.expander("Review coverage limitations"):
            for note in result.limitations:
                st.warning(note)
    report, citations = build_report(result)
    report_tab, register_tab, export_tab = st.tabs(
        ["Company research report", "Evidence & coverage", "Download research"]
    )
    with report_tab:
        st.markdown(report)
    with register_tab:
        st.dataframe(
            pd.DataFrame(
                [{k: v for k, v in asdict(d).items() if k != "passages"} for d in result.documents]
            ),
            hide_index=True,
            column_config={"url": st.column_config.LinkColumn("Official document")},
        )
        st.dataframe(
            pd.DataFrame([asdict(n) for n in result.news]),
            hide_index=True,
            column_config={"url": st.column_config.LinkColumn("News/disclosure")},
        )
        st.json(
            {
                "outcome": coverage,
                "stages": result.stages,
                "seconds": result.seconds,
                "news_feed": result.news_feed,
                "model_usage": result.model_usage,
            }
        )
        st.caption(
            "Document text may be untrusted. News is discovery-only unless the access label confirms selected source text was read. Inspect the supplied quotes and provenance before drawing conclusions."
        )
        with st.expander("Inspect citation register"):
            st.json(citations)
    with export_tab:
        st.download_button(
            "Download research report (.md)",
            report,
            "finsight-research.md",
            "text/markdown",
            on_click="ignore",
        )
        st.download_button(
            "Download research evidence bundle",
            report_bundle(result),
            "finsight-research.zip",
            "application/zip",
            on_click="ignore",
        )
        st.caption(
            "Bundle: report, citation register, document/news registers, evidence snapshot and financial workbook when supported. Review warnings remain in all applicable outputs."
        )
        st.download_button(
            "Download compact evidence for manual ChatGPT use",
            manual_synthesis_bundle(result, citations),
            "finsight-manual-synthesis.zip",
            "application/zip",
            on_click="ignore",
        )
        st.caption(
            "Manual pack: compact evidence.json, the existing synthesis instructions and a short guide. "
            "No API key or model call is needed. Review any chat-generated sample yourself; the app does not import chat responses."
        )
    with st.expander("Optional model narrative — separate API setup and spending approval"):
        st.write(
            "The deterministic report above works without a model. A chat subscription does not provide API access. No model call happens automatically."
        )
        if not api_key() or os.environ.get("FINSIGHT_ENABLE_MODEL") != "1":
            st.info(
                "AI synthesis is disabled. Search, source retrieval, financial calculations, citations "
                "and all report/evidence downloads work without a model API key. Only automatic "
                "narrative generation needs a configured provider and spending approval. "
                "Use Download research for the manual ChatGPT evidence pack. No model call was made here."
            )
            return
        try:
            config = ModelConfig.from_environment()
            if coverage["status"] == "failed":
                st.info(
                    "No substantive evidence: optional generation is unavailable for this failed run."
                )
                return
            evidence = build_model_evidence(result, citations)
            usage = estimate(config, evidence)
            st.json(usage)
            approved = st.checkbox(
                "I approve this model request and its displayed maximum estimated charge under my configured total cap"
            )
            if st.button("Generate optional narrative", disabled=not approved):
                provider = OpenAIProvider(
                    config,
                    Path(os.environ.get("FINSIGHT_CACHE_DIR", ".cache/sec")) / "model-usage.jsonl",
                )
                try:
                    st.session_state.research_narrative = provider.generate(
                        evidence, approved=approved
                    )
                except (ValueError, OSError) as exc:
                    st.error(str(exc))
            narrative = st.session_state.get("research_narrative")
            if narrative:
                st.subheader("Application-generated analysis — human review required")
                st.caption(
                    "Produced by the configured API provider; separate from the earlier assistant-written synthesis exercise."
                )
                st.warning(narrative["review"])
                for p in narrative["narrative"]["paragraphs"]:
                    st.text(f"{p['kind']}: {p['text']}")
                    st.caption("Citations: " + ", ".join(p["citation_ids"]))
                for claim in narrative["narrative"]["quantitative_claims"]:
                    st.text("Bound financial record: " + fact_text(claim))
                    st.caption("Citations: " + ", ".join(claim["citation_ids"]))
                st.json(narrative["usage"])
                st.download_button(
                    "Download optional model output",
                    json.dumps(narrative, indent=2),
                    "finsight-narrative.json",
                    "application/json",
                    on_click="ignore",
                )
                st.download_button(
                    "Download evidence and generated analysis",
                    report_bundle(result, narrative=narrative),
                    "finsight-research-with-analysis.zip",
                    "application/zip",
                    on_click="ignore",
                )
        except ValueError as exc:
            st.info(str(exc))
