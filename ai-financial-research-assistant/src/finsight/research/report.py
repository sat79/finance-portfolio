"""Cited deterministic research. Source excerpts are attributed, never treated as instructions."""

import html
import io
import json
import re
import zipfile
from dataclasses import asdict

from finsight.exports import csv_bytes, excel_bytes
from finsight.financials import calculate, commentary, review_notes
from finsight.models import LABELS, Metric
from finsight.research.evidence import excerpt, period_basis, recent_evidence, valid_date
from finsight.research.findings import key_findings
from finsight.research.models import Research
from finsight.research.outcomes import assess


def safe(text):
    return re.sub(r"([\\`*_{}\[\]()#+!|>])", r"\\\1", html.escape(str(text), quote=False))


def business_passages(document):
    """Prefer explicit business/product/revenue descriptions over generic risk matches."""
    groups = [
        r"^(?:The Company designs|Microsoft is a technology|Kaspi\.kz operates|NVIDIA pioneered)",
        r"^(?:We offer an array of services|Our products include|Our offerings include)",
        r"^(?:We generate .{0,40}revenue|We derive .{0,30}revenue|The Company.s advertising services include)",
        r"^(?:We operate our business and report|Our mission is)",
    ]
    selected = []
    for pattern in groups:
        for passage in document.passages:
            if 100 < len(passage.text) < 2000 and re.search(pattern, passage.text, re.I):
                if passage not in selected:
                    selected.append(passage)
                if len(selected) == 4:
                    return selected
                break
    return selected or excerpt(document, [r"business model", r"revenue.{0,50}from"], 2)


def build_report(research: Research) -> tuple[str, dict]:
    citations = {}

    def cite(key, url, locator, **metadata):
        previous = citations.get(key, {})
        if previous.get("quote", "").startswith(metadata.get("quote", "")) and len(
            previous.get("quote", "")
        ) > len(metadata.get("quote", "")):
            metadata["quote"] = previous["quote"]
            metadata["period_basis"] = previous.get("period_basis", "")
        citations[key] = {**citations.get(key, {}), "url": url, "locator": locator, **metadata}
        return f"[{key}]({url})"

    def quote(doc, passage, limit=1000):
        key = f"{doc.id}:B{doc.passages.index(passage) + 1}"
        # The excerpt is an exact prefix of normalized source text. Ellipsis is outside the quote.
        text = passage.text[:limit]
        reference = cite(
            key,
            doc.url,
            passage.locator,
            sha256=doc.sha256,
            quote=text,
            kind="disclosure excerpt",
            document_id=doc.id,
            document_kind=doc.kind,
            source_report_date=doc.period,
            publication_date=doc.published,
            period_basis=period_basis(text),
            retrieved_at=doc.retrieved_at,
        )
        return (
            f"> **Company disclosure excerpt:** “{safe(text)}”"
            + (" [excerpt truncated]" if len(passage.text) > limit else "")
            + f" {reference} — {safe(passage.locator)}; source report date: {safe(doc.period)}; duration cues: {safe(period_basis(text))}."
        )

    coverage = assess(research)
    company = research.company
    identity = cite(
        "IDENTITY", company.identity_url, "SEC company identity metadata", kind="identity"
    )
    lines = [
        f"# {safe(company.name)} — company research",
        f"**Research outcome: {coverage['status'].upper()}**. {safe(coverage['scope'])}",
        "Coverage gaps: " + safe("; ".join(coverage["missing"]) or "None in the bounded checks."),
        f"Research cut-off: **{research.cutoff.isoformat()}**. News window: **{research.news_start} to {research.news_end}**, inclusive (publication dates). Financial fiscal periods are listed separately; this is not historical point-in-time research.",
        f"{safe(company.ticker)} · {safe(company.exchange)} · CIK {company.cik} · business-address country: {safe(company.country)} · reporting currency: {safe(company.currency)}. {identity}",
        "**Method:** deterministic calculations and attributed source excerpts. No language-model narrative was generated. Reported figures are not universally verified. Source text is evidence, never application instructions.",
        "## Evidence coverage by source",
        "| Coverage | Actual outcome | Scope |",
        "|---|---|---|",
        f"| Official documents | {coverage['official_documents']['status']}; {coverage['official_documents']['read']}/{coverage['official_documents']['registered']} registered documents read | Bounded SEC and reviewed IR sources; not exhaustive |",
        f"| Financial extraction | {coverage['financial']['status']}; {coverage['financial']['observations']} selected observations | Annual extraction: AAPL, MSFT and KSPI only; interim text is not normalized financial data |",
        f"| Independent news | {coverage['independent_news']['label']}; {coverage['independent_news']['articles_with_cited_text']} articles with cited text from {coverage['independent_news']['discovered']} direct discoveries | One reviewed public publisher; headline metadata is not article text |",
        "## What the business does and how it earns revenue",
    ]
    findings_insert = len(lines) - 1
    annual = next(
        (d for d in research.documents if d.kind == "annual" and d.status == "read"), None
    )
    if annual:
        passages = business_passages(annual)
        lines.extend(quote(annual, p) for p in passages)
        if not passages:
            lines.append(
                "A business description could not be reliably selected. Review the annual report's business/segment sections."
            )
        lines.append(
            "These are the company's descriptions, not independent validation. Segment economics and revenue recognition need analyst review."
        )
    else:
        lines.append(
            "Annual-report text is missing or unreadable. Business-model analysis is incomplete; no generic company description was substituted."
        )

    lines.append("## Financial performance and comparable-period trends")
    data = research.dataset
    if data:
        lines.append(
            f"Accounting basis: {data.accounting_basis}. Amounts are whole reported currency units. {safe(data.policy)}"
        )
        lines += [
            "| Fiscal period | Metric | Reported value | Source | Review limitations |",
            "|---|---|---:|---|---|",
        ]
        for fact in data.selected:
            key = "F" + fact.id
            reference = cite(
                key,
                fact.source_url or company.identity_url,
                f"{fact.concept}; {fact.start or 'instant'} to {fact.end}; accession {fact.accession}",
                fact_id=fact.id,
                kind="reported financial observation",
                metric=fact.metric.value,
                value=str(fact.value),
                currency=fact.currency,
                period_start=str(fact.start) if fact.start else None,
                period_end=str(fact.end),
                unit=fact.unit,
                source_id=fact.source_id,
                warnings=list(review_notes(data, [fact])),
            )
            notes = review_notes(data, [fact])
            lines.append(
                f"| FY{fact.fiscal_year}, {fact.end} | {LABELS[fact.metric]} | {fact.value:,} {fact.currency} | {reference} | {safe('; '.join(notes)) or 'Not independently reviewed in this report'} |"
            )
        results = calculate(data)
        lines += [
            "",
            "### Deterministic calculations",
            "| Period end | Calculation | Value | Formula / inputs | Review limitations |",
            "|---|---|---:|---|---|",
        ]
        for c in results:
            references = " ".join(f"[F{key}]({citations['F' + key]['url']})" for key in c.input_ids)
            value = f"{c.value:,.4f} {c.unit}" if c.value is not None else "Unavailable"
            lines.append(
                f"| {c.period_end} | {c.metric} | {value} | {safe(c.formula)} {references} | {safe('; '.join(filter(None, [c.warning, *c.review_warnings])))} |"
            )
        lines.append("### Observations and comparability")
        for text in commentary(data, results):
            # Commentary is calculated from this table, with the same input references available above.
            lines.append(f"- **Calculated observation:** {safe(text)}")
        lines.append(
            "The observations above refer to the calculation table and its input citations. Margin changes are percentage points. Reported growth is not automatically organic growth."
        )
        lines.append("## Cash generation and financial position")
        latest = data.periods[-1].end
        lookup = {f.metric: f for f in data.selected if f.end == latest}
        for metric in (Metric.OPERATING_CASH_FLOW, Metric.CASH, Metric.ASSETS, Metric.LIABILITIES):
            fact = lookup.get(metric)
            if fact:
                lines.append(
                    f"- **Reported:** {LABELS[metric]} at/for {latest}: {fact.value:,} {fact.currency}. [F{fact.id}]({fact.source_url})"
                )
                for note in review_notes(data, [fact]):
                    lines.append(f"  **Review limitation:** {safe(note)}")
        if data.financial_group:
            lines.append(
                "**Analytical limitation:** lending/deposit cash flows and regulatory capital make conventional industrial-company FCF inappropriate here. CFO is not distributable cash; pretax profit is not operating profit. Group and parent-attributable profit remain separate. Assess capital adequacy, deposit funding, credit losses and restrictions before discussing distributions."
            )
        else:
            lines.append(
                "**Analytical interpretation:** CFO less PP&E purchases is a limited cash-generation proxy, not FCFF or a valuation input. Total liabilities are not all interest-bearing debt. Cash/assets/liabilities alone do not establish liquidity or solvency; maturities, commitments and restricted cash need review."
            )
    else:
        lines.extend(
            [
                "Financial extraction unavailable for this run. Company identification and document retrieval do not establish financial coverage.",
                "## Cash generation and financial position",
                "No supported quantitative assessment is available; no values or valuation inputs were invented.",
            ]
        )

    lines.append("## Management explanations for material changes")
    if annual:
        explanations = excerpt(
            annual,
            [
                r"(?:revenue|sales|income|cost|cash).{0,180}(?:increased|decreased|growth|decline).{0,140}(?:due to|driven by|reflect|primarily)",
                r"(?:increase|decrease).{0,150}primarily due",
            ],
            3,
        )
        lines.extend(quote(annual, p) for p in explanations)
        if not explanations:
            lines.append(
                "No reliably selected management explanation; do not infer causes from ratios alone."
            )
        lines.append(
            "**Review limitation:** these explanations relate to the annual disclosure's periods. They are not automatically explanations for a later interim period or every reported movement."
        )
    else:
        lines.append("Missing annual disclosure text prevents supported causal explanation.")

    lines.append("## Latest interim and earnings evidence alongside the annual baseline")
    lines.append(
        f"Annual baseline report date: {annual.period if annual else 'unavailable'}. "
        "The annual calculation table above is annual-only. The excerpts below are separate "
        "recent disclosure evidence, not additional normalized financial observations. "
        "Quarterly, year-to-date and annual amounts are not compared or annualized. "
        "A SEC current-report date can be an event date rather than a financial period end; "
        "use the quoted period headings. Missing duration/date context remains unresolved."
    )
    recent = recent_evidence(research.documents)
    for selection in recent:
        doc = selection["document"]
        lines.append(f"### {selection['label']} — {safe(doc.title)}")
        lines.extend(safe(warning) for warning in selection["date_warnings"])
        if selection["duplicate_document_ids"]:
            lines.append(
                "Equivalent selected supplementary text also appears in registered documents: "
                + ", ".join(selection["duplicate_document_ids"])
                + ". Quoted once here; their provenance remains in the document register."
            )
        lines.append(
            f"Filing/publication date: {doc.published}; SEC report-date metadata: {doc.period}; access: {doc.status}."
        )
        lines.append("#### Structured financial table evidence")
        lines.extend(safe(note) for note in doc.table_notes)
        if not doc.tables:
            lines.append(
                "No structured financial rows available. Old snapshots/unsupported formats are not reconstructed from flattened numbers."
            )
        for table in doc.tables:
            key = f"{doc.id}:T{table['table']}"
            reference = cite(
                key,
                doc.url,
                f"HTML table {table['table']}; source tag position {table['position']}",
                kind="structured table excerpt",
                table=table,
                sha256=doc.sha256,
                retrieved_at=doc.retrieved_at,
                source_report_date=doc.period,
            )
            lines.append(f"**Table {table['table']}: {safe(table['status'])}** {reference}")
            lines.append(" / ".join(safe(c["text"]) for c in table["context"]))
            groups = {}
            for row in table["rows"]:
                row_key = f"{key}:R{row['row']}"
                row_ref = cite(
                    row_key,
                    doc.url,
                    f"HTML table {table['table']}, row {row['row']}",
                    kind="structured table row",
                    table_id=key,
                    row_number=row["row"],
                    sha256=doc.sha256,
                    retrieved_at=doc.retrieved_at,
                )
                section = row["section"]["text"] if row["section"] else ""
                if row["status"] != "structured":
                    lines.append(
                        f"**{safe(row['label'])}** {row_ref}: ambiguous / unsupported — {safe(row['reason'])}; no column mapping supplied."
                    )
                    continue
                headings = tuple(
                    " / ".join(h["text"] for h in value["column_headers"])
                    for value in row["values"]
                )
                groups.setdefault(headings, []).append((row, row_ref, section))
            for headings, rows in groups.items():
                lines.append(
                    "| Source row / citation | "
                    + " | ".join(safe(h) for h in headings)
                    + " | Nearest preceding row heading |"
                )
                lines.append("|" + "---|" * (len(headings) + 2))
                for row, row_ref, section in rows:
                    lines.append(
                        f"| {safe(row['label'])} {row_ref} | "
                        + " | ".join(safe(v["value_cell"]["text"]) for v in row["values"])
                        + f" | {safe(section)} |"
                    )
            if groups:
                lines.append(
                    "Only identical source-header paths share a display grid. Row citations retain original cell coordinates/spans. A nearby row heading is context, not inferred segment membership."
                )
            lines.extend(safe(note) for note in table["notes"])
            if table.get("omitted_candidate_rows"):
                lines.append(
                    f"Row budget omitted {table['omitted_candidate_rows']} candidates: "
                    + safe(", ".join(table["omitted_row_labels"]))
                )
        if selection["passages"]:
            lines.append(
                "Selected passages and nearby period/section/unit context are quoted once below. Context does not assign a normalized period or scope to every figure."
            )
            for p in selection["passages"]:
                lines.append(quote(doc, p, limit=1600))
            for record in selection["records"]:
                key = f"{doc.id}:B{record['index'] + 1}"
                citations[key]["selection_topic"] = record["topic"]
                citations[key]["context_citation_ids"] = [
                    f"{doc.id}:B{i + 1}" for i in record["context_indices"]
                ]
            lines.append(
                "**Interpretation boundary:** these are source statements for the periods shown. "
                "Management explanations here are not assumed to explain annual movements. "
                "Check the exact duration, scope, units and accounting basis before comparing figures."
            )
        else:
            lines.append(
                "Recent document text is unavailable or no relevant passages were selected; no annual explanation was reused."
            )
    if not recent:
        lines.append(
            "No usable interim/earnings selection was established. Recent financial developments remain a coverage gap."
        )
    lines.append(
        "Selection is heuristic and limited to retrieved documents. Unread or undiscovered newer releases may change the assessment."
    )

    lines.append("## Recent developments and possible implications")
    if not research.news:
        lines.append(
            "No usable news evidence retrieved in the requested window. Coverage is incomplete; this does not establish that no material events occurred."
        )
    for item in research.news:
        reference = cite(
            item.id,
            item.url,
            "Selected source text" if item.content else "RSS headline metadata; article not read",
            kind=item.access,
            news=asdict(item),
        )
        lines.append(
            f"- **{safe(item.category)}:** {safe(item.title)} — {safe(item.publisher)}, {item.published[:10]}; event date: {item.event_date or 'not established'}. {reference} Access: {safe(item.access)}."
        )
        if not item.content:
            lines.append(
                "  **Discovery only:** no article/announcement content supplied for analysis. Read the original before drawing any substantive conclusion."
            )
            continue
        for content in item.content:
            reference = cite(
                content["citation_id"],
                content["url"],
                content["locator"],
                **{k: v for k, v in content.items() if k not in {"citation_id", "url", "locator"}},
            )
            lines.append(
                f"> **Read source excerpt:** “{safe(content['quote'])}” {reference} — {safe(content['locator'])}; duration cues: {safe(content['period_basis'])}."
            )
        if re.search(r"acqui|merger", item.title, re.I):
            question = "Investigate purchase price, financing, integration costs and reporting-scope changes; financial effects are not quantified here."
        elif re.search(r"earnings|results|revenue", item.title, re.I):
            question = "Compare disclosed results/guidance with the annual baseline, including period, scope and accounting basis; do not infer a forecast from the headline."
        elif re.search(r"regulat|lawsuit|antitrust", item.title, re.I):
            question = "Investigate the proceeding's status, possible remedies and disclosed contingencies; no loss probability or provision is inferred."
        elif re.search(r"ceo|chief|management", item.title, re.I):
            question = (
                "Review the leadership change and any disclosed strategy or execution implications."
            )
        else:
            question = "Read the original disclosure/article and determine whether cash flows, funding or business risk are materially affected."
        lines.append(f"  **Analyst question, not a reported outcome:** {question}")

    lines.append("## Principal risks, contradictions and unanswered questions")
    if annual:
        lines.extend(
            quote(annual, p)
            for p in excerpt(
                annual,
                [
                    r"(?:could|may).{0,100}(?:adverse|adversely|material|risk)",
                    r"(?:risk|uncertainty).{0,100}(?:business|operations|financial)",
                ],
                2,
            )
        )
    if data:
        for warning in data.warnings:
            lines.append(
                f"- **Source/review warning {safe(warning.code)}** ({warning.period_end or 'all periods'}, {warning.metric.value if warning.metric else 'all metrics'}): {safe(warning.message)}"
            )
    lines.extend(f"- {safe(note)}" for note in research.limitations)
    for doc in research.documents:
        if doc.status != "read" or doc.kind == "interim/amendment":
            lines.append(f"- {safe(doc.title)}: {doc.status}. {safe('; '.join(doc.limitations))}")
    lines.append(
        "Contradictory source observations are retained by the financial selector and flagged above; unresolved conflicts are not reconciled by prose. This report does not exhaustively detect contradictions in narrative documents or news. Which figures changed because of revisions, acquisitions, FX, inflation accounting or period length? Which notes or sources remain unread?"
    )
    lines.append("## Research conclusion and next investigation")
    lines.append(
        f"This report contains {len(data.selected) if data else 0} supported selected financial observations, {sum(d.status == 'read' for d in research.documents)} text-readable documents and {len(research.news)} news/disclosure items. It provides a sourced starting point, not an investment recommendation or a verified forecast."
    )
    if data:
        latest_results = [
            c
            for c in calculate(data)
            if c.period_end == data.periods[-1].end and c.value is not None
        ]
        for c in latest_results:
            refs = " ".join(f"[F{k}]({citations['F' + k]['url']})" for k in c.input_ids)
            lines.append(
                f"- **Calculated latest-period finding:** {c.metric} = {c.value:,.2f} {c.unit}. {refs}"
            )
        lines.append(
            "Calculation-specific warnings remain in the detailed financial table and source/review warnings above."
        )
    lines.append(
        "Next: resolve flagged disclosure/comparability issues, review the selected interim/earnings context and any missing releases, read discovery-only stories in full, and verify liquidity/capital and principal-risk notes before drawing stronger conclusions. Optional model narrative is a separate setup step; deterministic evidence and arithmetic remain available."
    )
    lines.append("## Document register")
    lines += [
        "| ID | Title | Period | Filing/publication date | Retrieved UTC | Status | SHA-256 |",
        "|---|---|---|---|---|---|---|",
    ]
    for doc in research.documents:
        lines.append(
            f"| {doc.id} | [{safe(doc.title)}]({doc.url}) | {doc.period} | {doc.published} | {doc.retrieved_at or 'Not retrieved'} | {doc.status} | {doc.sha256 or 'Unavailable'} |"
        )
        if (
            doc.retrieved_at
            and valid_date(doc.published) is not None
            and (research.cutoff.date() - valid_date(doc.published)).days > 450
        ):
            lines.append(
                f"\n**Stale disclosure warning:** {doc.id} publication is over 450 days before the research cut-off.\n"
            )
    finding_lines = [
        "## Key findings",
        "Company quotations are not independently verified. Findings are prioritized by evidence category, not exhaustive materiality. Calculations and open questions remain separate; full period/scope cautions are in the Finding interpretation notes below.",
    ]
    calc_map = {f"C{i}": c for i, c in enumerate(calculate(data), 1)} if data else {}
    findings = key_findings(research, recent)
    finding_context_seen = set()
    for index, finding in enumerate(findings, 1):
        finding_lines.append(f"### {index}. {safe(finding['title'])}")
        for key in finding["context_citation_ids"]:
            citation = citations[key]
            if key in finding_context_seen:
                continue
            finding_context_seen.add(key)
            finding_lines.append(
                f"**Nearby source context:** “{safe(citation['quote'])}” [{key}]({citation['url']})"
            )
        for statement in finding["statements"]:
            key = statement["citation_id"]
            finding_lines.append(
                f"**{statement['kind'].capitalize()} (verbatim):** “{safe(statement['text'])}” [{key}]({citations[key]['url']})"
            )
        for key in finding["calculation_ids"]:
            c = calc_map[key]
            references = " ".join(f"[F{i}]({citations['F' + i]['url']})" for i in c.input_ids)
            finding_lines.append(
                f"**Deterministic annual calculation:** {safe(c.metric.replace('_', ' '))} at {c.period_end}: {c.value:,.2f} {c.unit}. {references}"
            )
        if finding["calculation_ids"]:
            finding_lines.append(f"**Boundary:** {safe(finding['boundary'])}")
        question = finding["question"].split("?", 1)[0] + "?"
        finding_lines.append(f"**Unresolved analytical question:** {safe(question)}")
    if not findings:
        finding_lines.append(
            "Insufficient substantive evidence for prioritized findings; no finding was manufactured."
        )
    elif len(findings) < 3:
        finding_lines.append(
            "Fewer than three supported findings were available; the report does not fill missing evidence with generic conclusions."
        )
    lines[findings_insert:findings_insert] = finding_lines
    if findings:
        lines.append("## Finding interpretation notes")
        lines.append(
            "Full cautions retained for each summary finding; these notes do not establish semantic verification."
        )
        for finding in findings:
            lines.append(
                f"- **{safe(finding['title'])}:** {safe(finding['question'])} {safe(finding['boundary'])}"
            )
    lines.append("## Citation register")
    for key, value in citations.items():
        lines.append(f"- [{key}]({value['url']}): {safe(value['locator'])}")
    return "\n\n".join(lines).replace("|\n\n|", "|\n|"), citations


def report_bundle(research: Research) -> bytes:
    from finsight.research.model_evidence import build_model_evidence

    report, citations = build_report(research)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("research-report.md", report)
        archive.writestr("coverage.json", json.dumps(assess(research), indent=2))
        archive.writestr(
            "model-evidence.json", json.dumps(build_model_evidence(research, citations), indent=2)
        )
        archive.writestr("citations.json", json.dumps(citations, indent=2, default=str))
        snapshot = research.serializable()
        for doc in snapshot["documents"]:
            if doc["kind"] == "news original":
                for index, passage in enumerate(doc["passages"], 1):
                    passage["text"] = citations.get(f"{doc['id']}:B{index}", {}).get("quote", "")
                doc["limitations"].append(
                    "Export retains cited independent-article excerpts only. Empty blocks preserve original citation numbering; the URL/hash identify the retrieved original."
                )
        archive.writestr("research-evidence.json", json.dumps(snapshot, indent=2, default=str))
        archive.writestr(
            "document-register.csv",
            csv_bytes(
                [
                    {k: v for k, v in asdict(d).items() if k != "passages"}
                    for d in research.documents
                ]
            ),
        )
        archive.writestr("news.csv", csv_bytes([asdict(n) for n in research.news]))
        if research.dataset:
            archive.writestr(
                "financial-analysis.xlsx",
                excel_bytes(research.dataset, calculate(research.dataset)),
            )
    return output.getvalue()
