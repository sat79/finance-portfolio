"""Synthetic regressions for date ordering and the bounded public publisher route."""

from dataclasses import replace
from datetime import date
from types import SimpleNamespace

import pytest

from finsight.research.documents import extract
from finsight.research.evidence import recent_evidence
from finsight.research.models import Company, Document, Passage
from finsight.research.news import enrich_news
from finsight.research.publisher import discover_guardian, guardian_endpoint
from finsight.research.transport import EvidenceClient
from finsight.sec import SECError

ARTICLE = "https://www.theguardian.com/technology/2026/oct/20/apple-revenue-results"
TEXT = (
    "Apple reported higher revenue and profit in its financial results, according to the company. "
    "The figures cover the quarter ended in September and require comparison with the same period."
)
HTML = (
    "<nav>Apple revenue navigation is not article evidence.</nav>"
    '<div class="article-body-viewer-selector other"><p>' + TEXT + "</p></div>"
    "<footer>Unrelated profit story and donation appeal.</footer>"
).encode()


def release(published="2026-08-02", **kwargs):
    return Document(
        "SEC",
        "Earnings release",
        "earnings/event exhibit",
        ARTICLE,
        published,
        "2026-06-30",
        status="read",
        passages=[Passage("block 1", TEXT)],
        **kwargs,
    )


@pytest.mark.parametrize("undated", ["Not established", "", "2026-02-30", "2026-13-01", "nonsense"])
def test_undated_ir_cannot_displace_dated_release(undated):
    sec = release()
    ir = replace(sec, id="IR2", kind="IR linked document", published=undated)
    selected = recent_evidence([ir, sec])
    assert selected[0]["document"].id == "SEC"
    assert selected[0]["latest_eligible"]
    assert selected[1]["document"].id == "IR2"
    assert not selected[1]["latest_eligible"]
    assert selected[1]["passages"] and selected[1]["date_warnings"]
    assert "Supplementary" in selected[1]["label"]
    assert ("Invalid" in selected[1]["label"]) == (undated not in {"Not established", ""})


def test_interim_dates_are_calendar_dates_and_invalid_period_is_explicit():
    valid = replace(release(), title="10-Q — August", period="2026-06-30")
    invalid = replace(valid, id="bad", period="2026-99-99", published="2026-09-01")
    undated = replace(valid, id="unknown", period="2027-01-01", published="Not established")
    chosen = recent_evidence([invalid, undated, valid])
    assert chosen[0]["document"].id == "SEC"
    assert chosen[1]["document"].id == "unknown" and not chosen[1]["latest_eligible"]
    assert recent_evidence([invalid])[0]["date_warnings"]


@pytest.mark.parametrize(
    "url",
    [
        ARTICLE.replace("https:", "http:"),
        ARTICLE.replace("www.theguardian.com", "www.theguardian.com.evil.test"),
        ARTICLE.replace("www.theguardian.com", "user@www.theguardian.com"),
        ARTICLE.replace("www.theguardian.com", "www.theguardian.com:443"),
        ARTICLE + "?redirect=https://evil.test",
        ARTICLE + "#fragment",
        ARTICLE.replace("/20/", "/40/"),
        ARTICLE.replace("/oct/", "/xxx/"),
        "https://www.theguardian.com/technology/../private",
        "https://127.0.0.1/",
        "https://www.theguardian.com/technology/live/2026/oct/20/apple",
    ],
)
def test_publisher_route_rejects_unreviewed_urls_before_network(url, tmp_path):
    assert not guardian_endpoint(url)
    client = EvidenceClient(SimpleNamespace(cache_dir=tmp_path))
    with pytest.raises(SECError, match="outside"):
        client.get(url, refresh=True)
    assert client.attempts[0]["status"] == "failed"


def test_public_feed_to_article_retains_provenance_and_body_only():
    class Client:
        def __init__(self):
            self.calls = []

        def get(self, url, **kwargs):
            self.calls.append((url, kwargs))
            if url.endswith("/rss"):
                content = (
                    "<rss><channel><item><title>Apple revenue results</title><link>"
                    + ARTICLE
                    + "</link>"
                    "<pubDate>Tue, 20 Oct 2026 12:00:00 GMT</pubDate></item>"
                    "<item><title>Microsoft revenue</title><link>"
                    + ARTICLE.replace("apple", "microsoft")
                    + "</link>"
                    "<pubDate>Tue, 20 Oct 2026 12:00:00 GMT</pubDate></item>"
                    "<item><title>Apple revenue external link</title><link>https://evil.test/a</link>"
                    "<pubDate>Tue, 20 Oct 2026 12:00:00 GMT</pubDate></item>"
                    "</channel></rss>"
                ).encode()
                media = "application/xml"
            else:
                content, media = HTML, "text/html"
            return SimpleNamespace(
                content=content,
                media_type=media,
                fetched_at="2026-10-22T12:00:00+00:00",
                sha256="a" * 64,
                cached=False,
            )

    client = Client()
    company = Company("Apple Inc.", "AAPL", "Nasdaq", "0000320193")
    items, provenance = discover_guardian(
        client, company, date(2026, 10, 1), date(2026, 10, 22), refresh=True
    )
    assert len(items) == 1 and items[0].url == ARTICLE
    assert items[0].publisher == "The Guardian"
    assert items[0].discovery == provenance and not provenance["cached"]
    documents = []
    enrich_news(client, items, documents, refresh=True)
    assert len(client.calls) == 2 and all(kwargs["refresh"] for _, kwargs in client.calls)
    assert items[0].content[0]["quote"] == TEXT
    assert "selected_source_text_read" in items[0].access
    assert items[0].event_date is None and items[0].sha256 == "a" * 64
    assert [p.text for p in documents[0].passages] == [TEXT]


def test_publisher_consent_page_is_not_article_text():
    blocks, _, notes = extract(
        b"<p>Subscribe to read this Apple revenue article.</p>", "text/html", ARTICLE
    )
    assert blocks == [] and "unavailable" in notes[0]


def test_publisher_does_not_follow_redirects(tmp_path):
    class Session:
        def get(self, url, **kwargs):
            assert kwargs["allow_redirects"] is False
            assert "contact@example.com" not in kwargs["headers"]["User-Agent"]
            return self

        def __enter__(self):
            return SimpleNamespace(status_code=302)

        def __exit__(self, *args):
            return False

    client = EvidenceClient(
        SimpleNamespace(
            cache_dir=tmp_path, session=Session(), user_agent="FinSight contact@example.com"
        )
    )
    with pytest.raises(SECError, match="302"):
        client.get(ARTICLE, refresh=True)


def test_supplementary_dates_survive_report_and_model_without_completing_coverage(dataset):
    from test_research import report_fixture

    from finsight.research.model_evidence import build_model_evidence
    from finsight.research.outcomes import assess
    from finsight.research.report import build_report

    research = report_fixture(dataset)
    research.documents.append(replace(release("Not established"), kind="IR linked document"))
    report, _ = build_report(research)
    payload = build_model_evidence(research)
    assert "Supplementary evidence" in report and TEXT in report
    recent = payload["recent_disclosures"]
    assert len(recent) == 1 and not recent[0]["latest_eligible"] and recent[0]["date_warnings"]
    assert recent[0]["passages"][0]["quote"] == TEXT
    assert any("recent interim/earnings" in missing for missing in assess(research)["missing"])


def test_publisher_self_closing_break_keeps_article_scope():
    content = HTML.replace(b"<p>", b"<br/><p>")
    blocks, _, _ = extract(content, "text/html", ARTICLE)
    assert [p.text for p in blocks] == [TEXT]


def test_leadership_article_body_contributes_cited_evidence():
    """The live CEO story was extracted but dropped by the financial-only selector."""
    from finsight.research.models import NewsItem

    text = (
        "The new CEO introduced the company's products at its annual showcase. "
        "The leadership transition raises questions about the direction of the business."
    )

    class Client:
        def get(self, url, **kwargs):
            return SimpleNamespace(
                content=(
                    '<div class="article-body-viewer-selector"><p>' + text + "</p></div>"
                ).encode(),
                media_type="text/html",
                fetched_at="2026-10-23T02:00:00+00:00",
                sha256="a" * 64,
                cached=False,
            )

    item = NewsItem("leadership", "Apple CEO transition", "The Guardian", ARTICLE, "2026-10-20")
    documents = []
    enrich_news(Client(), [item], documents, refresh=True)
    assert item.content[0]["quote"] == text
    assert item.content[0]["citation_id"] == "NDocleadership:B1"
    assert item.content[0]["url"] == ARTICLE and item.sha256 == "a" * 64


@pytest.mark.parametrize(
    "failure",
    ["network_failure", "no_matching_article", "extraction_failure", "no_relevant_excerpt"],
)
def test_independent_coverage_distinguishes_failure_stages(dataset, failure):
    from test_research import report_fixture

    from finsight.research.models import NewsItem
    from finsight.research.outcomes import assess
    from finsight.research.report import build_report

    research = report_fixture(dataset)
    research.stages["Independent news"] = "partial: no relevant independent article discovered"
    if failure == "network_failure":
        research.stages["Independent news"] = "failed; earlier stages preserved"
        research.access_attempts = [
            {
                "url": "https://www.theguardian.com/technology/apple/rss",
                "status": "failed",
                "failure_kind": "network_failure",
            }
        ]
    if failure in {"extraction_failure", "no_relevant_excerpt"}:
        research.news = [NewsItem("N1", "Apple revenue", "The Guardian", ARTICLE, "2026-10-20")]
        research.documents.append(
            replace(
                release(),
                kind="news original",
                status="unreadable" if failure == "extraction_failure" else "read",
            )
        )
    coverage = assess(research)
    assert coverage["independent_news"]["status"] == failure
    assert coverage["independent_news"]["articles_with_cited_text"] == 0
    assert coverage["financial"]["observations"] == len(dataset.selected)
    assert coverage["official_documents"]["registered"] == 1
    report, _ = build_report(research)
    assert (
        "Evidence coverage by source" in report and coverage["independent_news"]["label"] in report
    )
    assert "AAPL, MSFT and KSPI only" in report


def test_transport_records_network_failure_without_claiming_extraction(tmp_path):
    import requests

    class Session:
        def get(self, *args, **kwargs):
            raise requests.exceptions.ProxyError("synthetic proxy denial")

    client = EvidenceClient(SimpleNamespace(cache_dir=tmp_path, session=Session()))
    with pytest.raises(SECError, match="connection failed"):
        client.get(ARTICLE, refresh=True)
    assert client.attempts[0]["failure_kind"] == "network_failure"
    assert "retrieved_at" not in client.attempts[0]


def test_invalid_publication_date_does_not_crash_report_staleness_check(dataset):
    from test_research import report_fixture

    from finsight.research.report import build_report

    research = report_fixture(dataset)
    research.documents.append(release("2026-02-30", retrieved_at="2026-10-23T02:00:00+00:00"))
    report, citations = build_report(research)
    assert "Invalid publication date" in report and "Supplementary evidence" in report
    assert citations["SEC:B1"]["publication_date"] == "2026-02-30"
