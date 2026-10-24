"""Evidence-based outcomes, independent of whether a renderer produced Markdown."""

from finsight.research.evidence import recent_evidence
from finsight.research.publisher import guardian_article, guardian_endpoint


def independent_coverage(research):
    """Separate discovery, source access, extraction and usable quoted evidence."""
    items = [n for n in research.news if guardian_article(n.url)]
    read = [n for n in items if n.content]
    stage = research.stages.get("Independent news", "not attempted")
    attempts = [a for a in research.access_attempts if guardian_endpoint(a["url"])]
    failed = [a for a in attempts if a["status"] == "failed"]
    docs = [d for d in research.documents if guardian_article(d.url)]
    if read:
        status = "selected_article_text_read"
    elif failed:
        status = failed[-1].get("failure_kind", "source_access_failure")
    elif any(d.status == "unreadable" for d in docs):
        status = "extraction_failure"
    elif any(d.status == "inaccessible" for d in docs):
        status = "article_access_failure"
    elif any(d.status == "read" for d in docs):
        status = "no_relevant_excerpt"
    elif not items and stage.startswith("partial: no relevant"):
        status = "no_matching_article"
    elif stage.startswith("failed"):
        status = "discovery_failure"
    else:
        status = "not_attempted" if stage == "not attempted" else "discovery_only"
    return {
        "status": status,
        "label": {
            "selected_article_text_read": "Selected original article text read",
            "network_failure": "Network request failed",
            "http_error": "Source returned an HTTP error",
            "source_failure": "Source retrieval failed",
            "source_access_failure": "Source access failed",
            "extraction_failure": "Article body extraction failed",
            "article_access_failure": "Original article inaccessible",
            "no_relevant_excerpt": "Body extracted; no relevant excerpt selected",
            "no_matching_article": "Feed retrieved; no matching article",
            "discovery_failure": "Feed discovery or parsing failed",
            "not_attempted": "Not attempted",
            "discovery_only": "Headline discovery only",
        }[status],
        "discovered": len(items),
        "articles_with_cited_text": len(read),
        "stage": stage,
        "scope": "One reviewed public publisher, one article maximum; not exhaustive independent coverage.",
    }


def assess(research):
    substantive = [
        d
        for d in research.documents
        if d.kind != "IR discovery"
        and d.status == "read"
        and any(len(p.text) > 80 for p in d.passages)
    ]
    financial = bool(research.dataset and research.dataset.selected)
    absent = set()
    missing = []
    if research.stages.get("Company resolution") != "completed":
        missing.append("Company resolution did not complete in this run.")
    if not any(d.kind == "annual" for d in substantive):
        missing.append("Annual baseline text is unavailable.")
    if not any(
        s["latest_eligible"] and any(len(p.text) > 80 for p in s["passages"])
        for s in recent_evidence(research.documents)
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
    if not any(n.content and guardian_article(n.url) for n in research.news):
        missing.append(
            "No independent original article text was read; independent news remains discovery-only or unavailable."
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
    official = [d for d in research.documents if d.kind != "news original"]
    official_read = sum(d.status == "read" for d in official)
    recent = any(s["latest_eligible"] and s["passages"] for s in recent_evidence(official))
    official_status = (
        "available"
        if official
        and official_read == len(official)
        and any(d.kind == "annual" for d in substantive)
        and recent
        else "partial"
        if any(d.kind != "news original" for d in substantive)
        else "unavailable"
    )
    return {
        "status": state,
        "missing": missing,
        "read_documents": len(substantive),
        "financial_observations": len(research.dataset.selected) if financial else 0,
        "official_documents": {
            "status": official_status,
            "read": official_read,
            "registered": len(official),
            "recent_passages_available": bool(recent),
        },
        "financial": {
            "status": "available"
            if financial and not absent
            else "partial"
            if financial
            else "unsupported"
            if not research.company.supported
            else "unavailable",
            "observations": len(research.dataset.selected) if financial else 0,
            "missing_latest_core_metrics": sorted(absent),
            "scope": "Reviewed annual extraction only: Apple (AAPL), Microsoft (MSFT), Kaspi.kz (KSPI). Interim figures remain quoted evidence.",
        },
        "independent_news": independent_coverage(research),
        "scope": "Complete means the bounded research checks passed, not exhaustive coverage or verified claims.",
    }
