"""Evidence-based outcomes, independent of whether a renderer produced Markdown."""

from finsight.research.evidence import recent_evidence


def assess(research):
    substantive = [
        d
        for d in research.documents
        if d.kind != "IR discovery"
        and d.status == "read"
        and any(len(p.text) > 80 for p in d.passages)
    ]
    financial = bool(research.dataset and research.dataset.selected)
    missing = []
    if research.stages.get("Company resolution") != "completed":
        missing.append("Company resolution did not complete in this run.")
    if not any(d.kind == "annual" for d in substantive):
        missing.append("Annual baseline text is unavailable.")
    if not any(
        any(len(p.text) > 80 for p in s["passages"]) for s in recent_evidence(research.documents)
    ):
        missing.append("No substantive recent interim/earnings passages are available.")
    unread = [d.id for d in research.documents if d.status != "read"]
    if unread:
        missing.append("Registered documents not read: " + ", ".join(unread))
    if not financial:
        missing.append("Reviewed financial extraction is unavailable or unsupported.")
    else:
        latest = max(p.end for p in research.dataset.periods)
        present = {f.metric.value for f in research.dataset.selected if f.end == latest}
        absent = {"revenue", "net_income", "operating_cash_flow"} - present
        if absent:
            missing.append(
                "Latest annual core financial coverage lacks: " + ", ".join(sorted(absent))
            )
    if research.stages.get("Recent news") != "completed":
        missing.append("Recent-news discovery did not complete.")
    if not any(n.content for n in research.news):
        missing.append(
            "No selected news/announcement content was read; headlines are discovery-only."
        )
    if any(
        v.startswith(("failed", "partial", "skipped", "unavailable"))
        for k, v in research.stages.items()
        if k != "Analysis"
    ):
        missing.append(
            "One or more evidence stages failed, were skipped or returned partial coverage."
        )
    # Identity, a fetched RSS feed, headings and a rendered template are not substantive research.
    state = "failed" if not substantive and not financial else "partial" if missing else "complete"
    return {
        "status": state,
        "missing": missing,
        "read_documents": len(substantive),
        "financial_observations": len(research.dataset.selected) if financial else 0,
        "scope": "Complete means the bounded research checks passed, not exhaustive coverage or verified claims.",
    }
