"""Stage boundaries retain completed evidence when a later provider fails."""

import time
from datetime import date, datetime, timezone

from finsight.research.documents import retrieve_documents, retrieve_ir, select_documents
from finsight.research.identity import resolve_details
from finsight.research.models import Research
from finsight.research.news import enrich_news, news_url, official_news, parse_news
from finsight.research.outcomes import assess
from finsight.research.transport import EvidenceClient
from finsight.sec import SECClient, SECError


def run_research(
    company,
    news_start: date,
    news_end: date,
    *,
    sec=None,
    evidence=None,
    progress=None,
    refresh=False,
):
    now = datetime.now(timezone.utc)
    if news_start > news_end or news_end > now.date() or (news_end - news_start).days > 365:
        raise ValueError(
            "Choose an ordered news range of at most 366 inclusive days, ending no later than today."
        )
    sec = sec or SECClient()
    evidence = evidence or EvidenceClient(sec)
    result = Research(company, now, news_start, news_end)
    started = time.perf_counter()

    def stage(name, function):
        result.stages[name] = "running"
        if progress:
            progress(name, result)
        before = time.perf_counter()
        try:
            outcome = function()
            result.stages[name] = outcome or "completed"
        except (SECError, ValueError, OSError, KeyError, TypeError) as exc:
            result.stages[name] = "failed; earlier stages preserved"
            result.limitations.append(f"{name}: {exc}")
        result.seconds[name] = round(time.perf_counter() - before, 3)
        if progress:
            progress(name, result)

    submissions = {}

    def identify():
        nonlocal submissions
        raw = sec._request(f"https://data.sec.gov/submissions/CIK{company.cik}.json", refresh)
        submissions = raw.data
        result.company = resolve_details(company, submissions)
        result.identity_evidence = {
            "url": result.company.identity_url,
            "retrieved_at": str(getattr(raw, "fetched_at", "")),
            "sha256": getattr(raw, "sha256", ""),
            "cached": getattr(raw, "cached", None),
        }

    stage("Company resolution", identify)

    def documents():
        docs, notes = select_documents(submissions, company.cik, now.date().isoformat())
        result.limitations.extend(notes)
        result.documents = retrieve_documents(evidence, docs, refresh=refresh)
        ir_docs, ir_notes = retrieve_ir(evidence, company.cik, refresh=refresh)
        result.documents.extend(ir_docs)
        result.limitations.extend(ir_notes)
        unread = sum(d.status != "read" for d in result.documents)
        if unread:
            result.limitations.append(
                f"{unread} registered documents were not read; document coverage incomplete."
            )
        result.limitations.append(
            "Evidence is limited to SEC recent filings and linked exhibits. Standalone IR-site documents/presentations are not exhaustively searched; inaccessible or unlinked presentations remain missing."
        )
        if not any(d.status == "read" and d.kind != "IR discovery" for d in result.documents):
            return "failed: no substantive documents read"
        if unread:
            return "partial: some registered documents unread"

    if result.stages["Company resolution"] == "completed":
        stage("Official documents", documents)
    else:
        result.stages["Official documents"] = "skipped: identity details unavailable"

    def news():
        result.news = official_news(result.documents, news_start, news_end)
        url = news_url(result.company, news_start, news_end)
        raw = evidence.get(url, refresh=refresh)
        result.news_feed = {
            "url": url,
            "retrieved_at": raw.fetched_at,
            "sha256": raw.sha256,
            "cached": raw.cached,
        }
        items = parse_news(raw.content, news_start, news_end)
        result.news.extend(sorted(items, key=lambda item: item.published, reverse=True)[:12])
        result.limitations.append(
            "Independent news is RSS headline metadata only: articles/paywalled text were not read. A company-name and financial-event keyword search can miss events or include namesakes; relevance needs review. Coverage is incomplete and not exhaustive; zero results does not establish no news."
        )
        if len(items) > 12:
            result.limitations.append(
                "News budget: 12 most recently published feed stories retained after deduplication; additional stories omitted. Coverage is incomplete."
            )

    stage("Recent news", news)
    if result.stages["Recent news"] != "completed":
        result.limitations.append(
            "Independent news retrieval failed. Coverage is incomplete; do not infer an absence of events."
        )
    enrich_news(evidence, result.news, result.documents, refresh=refresh)

    def financials():
        if not company.supported:
            result.limitations.append(
                "Company identified, but financial extraction is not supported for this CIK. Reviewed financial profiles cover KSPI, Apple and Microsoft only; no figures substituted."
            )
            return
        result.dataset = sec.load(company.ticker, refresh=refresh)

    stage("Financial extraction", financials)
    if result.dataset is None or not result.dataset.selected:
        result.stages["Financial extraction"] = "unavailable: see coverage limitations"
    result.access_attempts = list(getattr(sec, "attempts", [])) + list(
        getattr(evidence, "attempts", [])
    )
    result.stages["Analysis"] = (
        assess(result)["status"] + ": evidence assessment; report rendering follows"
    )
    result.seconds["total"] = round(time.perf_counter() - started, 3)
    return result
