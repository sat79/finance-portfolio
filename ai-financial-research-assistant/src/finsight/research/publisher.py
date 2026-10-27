"""One free, public publisher route; no Google wrapper decoding or paywall bypass."""

import re
from datetime import date
from urllib.parse import urlsplit

GUARDIAN_FEEDS = {
    "0000320193": "https://www.theguardian.com/technology/apple/rss",
    "0000789019": "https://www.theguardian.com/technology/microsoft/rss",
    "0001985487": "https://www.theguardian.com/business/banking/rss",
}


def guardian_article(url):
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "www.theguardian.com"
        or parsed.query
        or parsed.fragment
    ):
        return False
    match = re.fullmatch(
        r"/(?:technology|business)/([0-9]{4})/([a-z]{3})/([0-9]{2})/([a-z0-9]+(?:-[a-z0-9]+)*)",
        parsed.path,
    )
    if not match:
        return False
    try:
        month = "jan feb mar apr may jun jul aug sep oct nov dec".split().index(match[2]) + 1
        date(int(match[1]), month, int(match[3]))
    except ValueError:
        return False
    return True


def guardian_endpoint(url):
    return url in GUARDIAN_FEEDS.values() or guardian_article(url)


def discover_guardian(client, company, start, end, *, refresh=False):
    from finsight.research.news import parse_news

    url = GUARDIAN_FEEDS.get(company.cik)
    if not url:
        return [], {
            "status": "unsupported",
            "reason": "No reviewed publisher feed for this entity.",
        }
    raw = client.get(url, refresh=refresh)
    provenance = {
        "url": url,
        "retrieved_at": raw.fetched_at,
        "sha256": raw.sha256,
        "cached": raw.cached,
        "status": "retrieved",
        "scope": "Public RSS feed only; not an archive search. Relevant older stories may be absent.",
    }
    company_pattern = {
        "0000320193": r"\bApple\b",
        "0000789019": r"\bMicrosoft\b",
        "0001985487": r"\bKaspi(?:\.kz)?\b",
    }[company.cik]
    items = []
    for item in parse_news(raw.content, start, end):
        if (
            guardian_article(item.url)
            and re.search(company_pattern, item.title, re.I)
            and re.search(
                r"earnings|revenue|profit|sales|acqui|financ|regulat|lawsuit|antitrust|competition|CEO|dividend|guidance|jobs|cuts|invest|billion|million",
                item.title,
                re.I,
            )
        ):
            item.publisher = "The Guardian"
            item.category = "independent reporting; public publisher RSS discovery"
            item.discovery = dict(provenance)
            items.append(item)
    return sorted(items, key=lambda n: n.published, reverse=True)[:3], provenance
