"""Public RSS discovery is metadata evidence, never a claim to have read an article."""

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode, urlsplit

from finsight.research.models import Document, NewsItem
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
                    old.category == item.category
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
                for p in doc.passages
                if 30 < len(p.text) < 250
                and re.search(r"announces|reports|results|acquisition|presentation", p.text, re.I)
            ),
            doc.title,
        )
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
