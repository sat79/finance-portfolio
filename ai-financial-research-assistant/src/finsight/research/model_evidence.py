"""One auditable payload for optional narration; no URL-only claim support."""

from copy import deepcopy
from dataclasses import asdict

from finsight.financials import calculate, review_notes
from finsight.research.evidence import recent_evidence
from finsight.research.findings import key_findings
from finsight.research.outcomes import assess
from finsight.research.report import build_report


def compact_synthesis_evidence(full):
    """Subset the existing selected findings; no new selection rules or claim permissions."""
    result = deepcopy(full)
    refs, quantitative_ids = set(), set()
    for finding in result["key_findings"]:
        refs.update(finding["context_citation_ids"])
        refs.update(s["citation_id"] for s in finding["statements"])
        quantitative_ids.update(finding["calculation_ids"])
        # Quote text lives once in the citation register.
        finding["statements"] = list(
            {
                s["citation_id"]: {"kind": s["kind"], "citation_id": s["citation_id"]}
                for s in finding["statements"]
            }.values()
        )
    calculations = [c for c in result["calculations"] if c["evidence_id"] in quantitative_ids]
    for c in calculations:
        quantitative_ids.update("F" + key for key in c["input_ids"])
    quantitative = {
        k: v for k, v in result["quantitative_evidence"].items() if k in quantitative_ids
    }
    for claim in quantitative.values():
        refs.update(claim["citation_ids"])
    doc_ids = {r["document_id"] for r in result["recent_disclosures"] if r["latest_eligible"]}
    news = [n for n in result["news"] if n["content"] and n["document_id"] in doc_ids][:3]
    for n in news:
        for content in n["content"]:
            refs.add(content["citation_id"])
    citations = {
        k: v for k, v in result["citations"].items() if k in refs and v["eligible_for_prose"]
    }
    if refs - citations.keys():
        raise ValueError("Compact evidence contains a missing or ineligible citation.")
    for value in citations.values():
        if value.get("quote") == value["support_text"]:
            value.pop("quote", None)
    for n in news:
        n["content"] = [{"citation_id": c["citation_id"]} for c in n["content"]]
    recent = []
    for doc in result["recent_disclosures"]:
        doc["passages"] = [p for p in doc["passages"] if p["citation_id"] in refs]
        if doc["passages"]:
            doc.pop("table_citation_ids", None)
            doc.pop("table_notes", None)
            recent.append(doc)
    result["coverage"]["tables"].pop("documents", None)
    result.update(
        citations=citations,
        quantitative_evidence=quantitative,
        calculations=calculations,
        selected_financial_observations=[
            f
            for f in result["selected_financial_observations"]
            if f["evidence_id"] in quantitative_ids
        ],
        news=news,
        recent_disclosures=recent,
        evidence_layout="Compact pilot subset of existing key findings and their annual calculation inputs. Quotes resolve to citations.support_text; news content references the same register. Full evidence remains in the source bundle. All warnings and coverage summaries retained. No table or discovery-only content can support claims.",
    )
    return result


def build_model_evidence(research, citations=None):
    if citations is None:
        _, citations = build_report(research)
    citations = {key: dict(value) for key, value in citations.items()}
    observations, calculations, quantitative = [], [], {}
    warning_registry = {}

    def warning_ids(messages):
        ids = []
        for message in messages:
            key = next((k for k, v in warning_registry.items() if v == message), None)
            if key is None:
                key = f"W{len(warning_registry) + 1}"
                warning_registry[key] = message
            ids.append(key)
        return ids

    data = research.dataset
    if data:
        for fact in data.selected:
            key = "F" + fact.id
            row = {
                "evidence_id": key,
                "metric": fact.metric.value,
                "value": str(fact.value),
                "period_start": str(fact.start) if fact.start else None,
                "period_end": str(fact.end),
                "currency": fact.currency,
                "unit": fact.unit,
                "citation_ids": [key],
                "source_urls": [fact.source_url],
            }
            quantitative[key] = row
            observations.append(
                {
                    **fact.model_dump(mode="json"),
                    "evidence_id": key,
                    "review_warning_ids": warning_ids(review_notes(data, [fact])),
                }
            )
            citations[key]["support_text"] = fact_text(row)
        for index, calc in enumerate(calculate(data), 1):
            row = calc.model_dump(mode="json")
            row["review_warning_ids"] = warning_ids(row.pop("review_warnings", []))
            row["evidence_id"] = f"C{index}"
            calculations.append(row)
            if calc.value is None:
                continue
            inputs = [f for f in data.selected if f.id in calc.input_ids]
            periods = [p for p in data.periods if p.end == calc.period_end]
            quantitative[row["evidence_id"]] = {
                "evidence_id": row["evidence_id"],
                "metric": calc.metric,
                "value": str(calc.value),
                "period_start": str(periods[0].start) if periods else None,
                "period_end": str(calc.period_end),
                "currency": inputs[0].currency if inputs else None,
                "unit": calc.unit,
                "citation_ids": ["F" + f.id for f in inputs],
                "source_urls": list(dict.fromkeys(f.source_url for f in inputs)),
            }
    for value in citations.values():
        if "news" in value:
            value["news_id"] = value["news"]["id"]
            value["news"] = {"publisher": value["news"]["publisher"]}
        if "warnings" in value:
            value["warning_ids"] = warning_ids(value.pop("warnings"))
        value["support_text"] = value.get("quote") or value.get("support_text", "")
        # Headline and identity metadata are context, not evidence for substantive model prose.
        value["eligible_for_prose"] = bool(value["support_text"])
    recent = []
    for selected in recent_evidence(research.documents):
        doc = selected["document"]
        recent.append(
            {
                "label": selected["label"],
                "latest_eligible": selected["latest_eligible"],
                "date_warnings": selected["date_warnings"],
                "duplicate_document_ids": selected["duplicate_document_ids"],
                "document_id": doc.id,
                "source_report_date": doc.period,
                "publication_date": doc.published,
                "status": doc.status,
                "table_citation_ids": [f"{doc.id}:T{t['table']}" for t in doc.tables],
                "table_notes": doc.table_notes
                or [
                    "No original structural table evidence available; flattened numbers are not reconstructed."
                ],
                "passages": [
                    {
                        "citation_id": f"{doc.id}:B{doc.passages.index(p) + 1}",
                    }
                    for p in selected["passages"]
                ],
            }
        )
    return {
        "selection_budget": {
            "latest_documents": 2,
            "supplementary_documents": 2,
            "primary_passages_per_latest": 6,
            "context_passages_per_primary": 3,
            "max_passage_characters": 1600,
            "max_key_findings": 5,
        },
        "evidence_layout": "Recent passage references resolve to the single citation register, which contains actual source quotes, locators and provenance. Warning IDs resolve to warning_registry; no warning is omitted.",
        "table_policy": "Structured table records preserve source cell geometry, column headings and units. They are not normalized financial observations or eligible free-prose/numerical claim records. Ambiguous/unsupported layouts are explicit; no annual substitution or currency inference.",
        "warning_registry": warning_registry,
        "key_findings": key_findings(research),
        "company": asdict(research.company),
        "identity_evidence": research.identity_evidence,
        "research_cutoff": research.cutoff.isoformat(),
        "news_window": {"start": str(research.news_start), "end": str(research.news_end)},
        "coverage": assess(research),
        "news": [asdict(n) for n in research.news],
        "recent_disclosures": recent,
        "citations": citations,
        "selected_financial_observations": observations,
        "calculations": calculations,
        "quantitative_evidence": quantitative,
        "financial_warnings": [w.model_dump(mode="json") for w in data.warnings] if data else [],
        "limitations": research.limitations,
        "claim_policy": "Numerical claims must copy an exact quantitative_evidence record; render them deterministically. Prose is unverified and requires exact supporting excerpts. Discovery-only news cannot support substantive claims.",
    }


def fact_text(claim):
    return (
        f"{claim['metric']} | {claim['period_start'] or 'instant'} to {claim['period_end']} | "
        f"{claim['value']} {claim['unit']} | currency {claim['currency']}"
    )
