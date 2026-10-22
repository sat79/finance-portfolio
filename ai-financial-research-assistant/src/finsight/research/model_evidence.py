"""One auditable payload for optional narration; no URL-only claim support."""

from dataclasses import asdict

from finsight.financials import calculate, review_notes
from finsight.research.evidence import recent_evidence
from finsight.research.outcomes import assess
from finsight.research.report import build_report


def build_model_evidence(research, citations=None):
    if citations is None:
        _, citations = build_report(research)
    citations = {key: dict(value) for key, value in citations.items()}
    observations, calculations, quantitative = [], [], {}
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
                    "review_warnings": list(review_notes(data, [fact])),
                }
            )
            citations[key]["support_text"] = fact_text(row)
        for index, calc in enumerate(calculate(data), 1):
            row = calc.model_dump(mode="json")
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
                "document_id": doc.id,
                "source_report_date": doc.period,
                "publication_date": doc.published,
                "status": doc.status,
                "passages": [
                    {
                        "citation_id": f"{doc.id}:B{doc.passages.index(p) + 1}",
                        **citations[f"{doc.id}:B{doc.passages.index(p) + 1}"],
                    }
                    for p in selected["passages"]
                ],
            }
        )
    return {
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
