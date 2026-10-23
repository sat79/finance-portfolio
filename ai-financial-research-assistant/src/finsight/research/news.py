"""Public RSS discovery is metadata evidence, never a claim to have read an article."""

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode, urlsplit

from finsight.research.evidence import is_interim
from finsight.research.models import Document, NewsItem
from finsight.research.publisher import guardian_article
from finsight.sec import SECError

ALIASES = {"0000320193": "Apple", "0000789019": "Microsoft", "0001985487": "Kaspi.kz"}


def news_url(company, start: date, end: date):
    name = ALIASES.get(company.cik, company.name)
    query = (
        f'"{name}" (earnings OR revenue OR acquisition OR financing OR regulation '
        f"OR lawsuit OR management OR CEO OR dividend OR guidance) "
        f"after:{(start - timedelta(days=1)).isoformat()} before:{(end + timedelta(days=1)).isoformat()}"
    )
    return "https://news.google.com/rss/search?" + urlencode(
        {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    )


def title_key(title):
    return set(re.findall(r"[a-z0-9]+", title.casefold().rsplit(" - ", 1)[0]))


def deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    kept = []
    for item in items:
        key = title_key(item.title)
        duplicate = next(
            (
                old
                for old in kept
                if old.url == item.url
                or (
                    (
                        old.category == item.category
                        or (
                            old.category.startswith("independent reporting")
                            and item.category.startswith("independent reporting")
                        )
                    )
                    and abs(
                        (
                            date.fromisoformat(old.published[:10])
                            - date.fromisoformat(item.published[:10])
                        ).days
                    )
                    <= 3
                    and key
                    and len(key & title_key(old.title)) / len(key | title_key(old.title)) >= 0.82
                )
            ),
            None,
        )
        if duplicate:
            if item.url != duplicate.url:
                duplicate.duplicate_urls.append(item.url)
        else:
            kept.append(item)
    return kept


def parse_news(content: bytes, start: date, end: date) -> list[NewsItem]:
    if (
        len(content) > 2 * 1024 * 1024
        or b"<!DOCTYPE" in content.upper()
        or b"<!ENTITY" in content.upper()
    ):
        raise SECError("News feed exceeds size limit or contains unsupported XML declarations.")
    try:
        root = ET.fromstring(content)
        if root.tag != "rss":
            raise ValueError
        items = []
        for row in root.findall("./channel/item"):
            title, url = row.findtext("title", "").strip(), row.findtext("link", "").strip()
            published = parsedate_to_datetime(row.findtext("pubDate", ""))
            published = published.replace(tzinfo=published.tzinfo or timezone.utc).astimezone(
                timezone.utc
            )
            if not start <= published.date() <= end:
                continue
            if not title or urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
                continue
            publisher = row.findtext("source", "Unknown publisher")
            category = (
                "company/press-release distribution (metadata only)"
                if re.search(r"business wire|pr newswire|globenewswire|newsroom", publisher, re.I)
                else "independent reporting (feed metadata only)"
            )
            items.append(
                NewsItem(
                    "N" + hashlib.sha256(url.encode()).hexdigest()[:10],
                    title[:500],
                    publisher,
                    url,
                    published.isoformat(),
                    category=category,
                )
            )
        return deduplicate(items)
    except (ET.ParseError, TypeError, ValueError, OverflowError) as exc:
        raise SECError("News feed has invalid dates/schema; coverage incomplete.") from exc


def official_news(documents: list[Document], start: date, end: date):
    items = []
    for doc in documents:
        if (
            doc.kind != "earnings/event exhibit"
            or not start.isoformat() <= doc.published <= end.isoformat()
        ):
            continue
        title = next(
            (
                p.text
                for p in doc.passages[:20]
                if 30 < len(p.text) < 250
                and re.search(r"announces|reports|results|acquisition|presentation", p.text, re.I)
            ),
            doc.title,
        )
        if is_interim(doc):
            title = "Interim financial disclosure — " + doc.published
        items.append(
            NewsItem(
                "N" + doc.id,
                title,
                "Company disclosure via SEC",
                doc.url,
                doc.published,
                category="company announcement; date is SEC filing date",
                access="extracted_document" if doc.status == "read" else "document_not_read",
                document_id=doc.id,
            )
        )
    return deduplicate(items)


def enrich_news(client, items, documents, *, refresh=False, limit=3):
    """Read a small selection of official disclosures or already permitted original URLs.

    Google RSS wrapper URLs are not article text. No wrapper decoding, paywall
    bypass, arbitrary-host fetches or automatic redirects are attempted.
    """
    from finsight.research.documents import read_document
    from finsight.research.evidence import excerpt, period_basis, recent_evidence

    used = 0
    independent_used = False
    # Reserve a slot for the narrow independent route even when official releases are newer.
    for item in sorted(items, key=lambda n: (guardian_article(n.url), n.published), reverse=True):
        item.content = []
        doc = next((d for d in documents if d.id == item.document_id), None)
        if doc and is_interim(doc):
            item.title = "Interim financial disclosure — " + doc.published
            item.category = "company interim financial disclosure; date is SEC filing date"
        if guardian_article(item.url):
            if independent_used:
                item.access = "discovery_only; independent article budget exhausted"
                continue
            independent_used = True
        if used >= limit:
            item.access = "discovery_only; selected-content budget exhausted"
            continue
        if doc is None:
            parsed = urlsplit(item.url)
            if parsed.hostname == "news.google.com":
                item.access = "discovery_only; article not read"
                item.access_notes.append(
                    "RSS aggregator link does not establish an accessible original article URL."
                )
                continue
            # EvidenceClient enforces the reviewed host/path allowlist before any request.
            doc = Document(
                "NDoc" + item.id,
                item.title,
                "news original",
                item.url,
                item.published[:10],
                "Not established",
            )
            used += 1
            read_document(client, doc, refresh=refresh)
            documents.append(doc)
            item.document_id = doc.id
        else:
            used += 1
        item.retrieved_at, item.sha256 = doc.retrieved_at, doc.sha256
        if doc.status != "read":
            item.access = "discovery_only; original source not read"
            item.access_notes.extend(doc.limitations)
            continue
        passages = excerpt(
            doc,
            [
                r"revenue|earnings|profit|sales|results|acquisition|financing|regulat|management|dividend|outlook|lawsuit|antitrust|competition|invest|billion|million|\bCEO\b|chief executive|leadership"
            ],
            2,
        )
        if is_interim(doc):
            passages = [p for p in recent_evidence([doc])[0]["passages"] if len(p.text) > 80][:2]
        if not passages:
            item.access = "discovery_only; no relevant content selected"
            continue
        # Only explicit past meeting/resolution dates; never infer event date from filing date.
        for passage in doc.passages[:20]:
            match = re.search(
                r"(?:resolutions were duly passed.{0,80}? on|meeting (?:was )?held on)\s+(\d{1,2} [A-Za-z]+ \d{4})",
                passage.text[:1000],
                re.I,
            )
            if match:
                try:
                    event_date = datetime.strptime(match[1], "%d %B %Y").date()
                    if event_date > date.fromisoformat(item.published[:10]):
                        continue
                    item.event_date = event_date.isoformat()
                    item.event_date_source = {
                        "citation_id": f"{doc.id}:B{doc.passages.index(passage) + 1}",
                        "quote": passage.text[:1000],
                    }
                    if passage not in passages:
                        passages.append(passage)
                    break
                except ValueError:
                    continue
        item.content = [
            {
                "citation_id": f"{doc.id}:B{doc.passages.index(p) + 1}",
                "quote": p.text[:1000],
                "url": doc.url,
                "locator": p.locator,
                "document_id": doc.id,
                "source_report_date": doc.period,
                "period_basis": period_basis(p.text),
                "sha256": doc.sha256,
                "retrieved_at": doc.retrieved_at,
            }
            for p in passages
        ]
        item.access = "selected_source_text_read; not independently verified"
        item.access_notes.append(
            "Only the supplied source excerpts support analysis; publication/filing date is not an inferred event date."
        )
    return items
