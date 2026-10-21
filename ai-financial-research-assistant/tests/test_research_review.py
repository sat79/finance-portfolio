"""Regression tests for the independent review, using explicitly synthetic evidence."""

from copy import deepcopy
from dataclasses import replace
from datetime import date
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest
from test_app import APP
from test_research import NOW, URL, report_fixture, submissions

from finsight.research.evidence import recent_evidence
from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import Document, NewsItem, Passage
from finsight.research.narrative import validate_narrative
from finsight.research.news import enrich_news, official_news
from finsight.research.outcomes import assess
from finsight.research.report import build_report
from finsight.research.workflow import run_research
from finsight.sec import SECError


@pytest.fixture
def research(dataset):
    result = report_fixture(dataset)
    interim = Document(
        "D2",
        "10-Q — 2026-08-01",
        "interim/amendment",
        URL.replace("report.htm", "interim.htm"),
        "2026-08-01",
        "2026-06-30",
        NOW.isoformat(),
        "b" * 64,
        "read",
        [
            Passage(
                "HTML text block 1",
                "Three months ended June 30, 2026 and six months ended June 30, 2026",
            ),
            Passage(
                "HTML text block 2",
                "Revenue increased in the three months ended June 30, 2026 primarily due to subscriptions. Six-month year-to-date amounts cover a different duration and must not be treated as quarterly results.",
            ),
        ],
    )
    earnings = Document(
        "E3",
        "Exhibit: quarterly earnings release",
        "earnings/event exhibit",
        URL.replace("report.htm", "earnings.htm"),
        "2026-08-02",
        "2026-08-02",
        NOW.isoformat(),
        "c" * 64,
        "read",
        [
            Passage(
                "HTML text block 1",
                "Company announces financial results for the quarter ended June 30, 2026. Revenue increased primarily due to subscriptions, according to management. The source explains the reporting period; filing date is later.",
            ),
        ],
    )
    result.documents += [interim, earnings]
    result.news_start, result.news_end = date(2026, 7, 1), date(2026, 10, 18)
    result.news = official_news(result.documents, result.news_start, result.news_end)
    enrich_news(None, result.news, result.documents)
    result.stages = {
        s: "completed"
        for s in ["Company resolution", "Official documents", "Recent news", "Financial extraction"]
    }
    return result


def test_outcomes_require_substantive_evidence(research):
    assert assess(research)["status"] == "complete"
    research.documents[1].status = "inaccessible"
    assert assess(research)["status"] == "partial"
    assert any("D2" in gap for gap in assess(research)["missing"])
    research.documents = []
    research.dataset = None
    # A successfully fetched feed or resolved name is not a successfully researched company.
    research.news = [
        NewsItem(
            "N1",
            "A headline",
            "Publisher",
            "https://news.google.com/rss/articles/test",
            "2026-08-01",
        )
    ]
    assert assess(research)["status"] == "failed"
    report, _ = build_report(research)
    assert "Research outcome: FAILED" in report
    assert "Discovery only" in report
    assert "Investigate purchase price" not in report


def test_all_network_stages_failed_never_report_success(research):
    class Failure:
        def _request(self, *args, **kwargs):
            raise SECError("blocked")

        def get(self, *args, **kwargs):
            raise SECError("blocked")

        def load(self, *args, **kwargs):
            raise SECError("blocked")

    result = run_research(
        research.company, research.news_start, research.news_end, sec=Failure(), evidence=Failure()
    )
    assert assess(result)["status"] == "failed"
    assert result.stages["Analysis"].startswith("failed")
    assert result.dataset is None and not result.documents


def test_registered_but_unread_documents_are_not_a_success(research):
    class SEC:
        def _request(self, *args):
            return SimpleNamespace(data=submissions())

        def load(self, *args, **kwargs):
            return research.dataset

    class Evidence:
        def get(self, *args, **kwargs):
            raise SECError("HTTP 403")

    result = run_research(
        research.company, research.news_start, research.news_end, sec=SEC(), evidence=Evidence()
    )
    assert result.stages["Official documents"].startswith("failed")
    assert assess(result)["status"] == "partial"
    assert result.dataset is research.dataset


def test_latest_interim_and_earnings_enter_report_and_payload(research):
    report, citations = build_report(research)
    assert (
        "Latest interim filing" in report
        and "Latest accessible earnings/results disclosure" in report
    )
    assert "Three months ended June 30, 2026 and six months ended June 30, 2026" in report
    assert "not compared or annualized" in report
    assert "Annual baseline report date: 2025-12-31" in report
    assert citations["D2:B2"]["source_report_date"] == "2026-06-30"
    assert "quarterly" in citations["D2:B2"]["period_basis"]
    assert "year-to-date" in citations["D2:B2"]["period_basis"]
    payload = build_model_evidence(research)
    assert payload["company"]["cik"] == research.company.cik
    assert payload["research_cutoff"] == research.cutoff.isoformat()
    assert payload["recent_disclosures"][0]["passages"][1]["quote"] in report
    assert payload["news"][0]["content"] and payload["news"][0]["publisher"]
    assert payload["news"][0]["event_date"] is None
    assert payload["selected_financial_observations"] and payload["calculations"]
    assert "financial_warnings" in payload and "review_warnings" in payload["calculations"][0]
    for record in payload["recent_disclosures"]:
        for passage in record["passages"]:
            assert passage["citation_id"] in payload["citations"]


def test_latest_unread_interim_does_not_silently_fall_back(research):
    research.documents.append(
        replace(
            research.documents[1],
            id="D4",
            period="2026-09-30",
            published="2026-11-01",
            status="inaccessible",
            passages=[],
        )
    )
    selected = recent_evidence(research.documents)[0]
    assert selected["document"].id == "D4" and not selected["passages"]
    report, _ = build_report(research)
    assert "no annual explanation was reused" in report


def test_news_metadata_never_masquerades_as_read_content(research):
    item = NewsItem(
        "N9",
        "Company acquisition",
        "Independent publisher",
        "https://news.google.com/rss/articles/test",
        "2026-08-03",
        event_date="2026-08-01",
    )
    research.news.append(item)
    enrich_news(None, research.news, research.documents)
    assert not item.content and "discovery_only" in item.access
    payload = build_model_evidence(research)
    news = next(n for n in payload["news"] if n["id"] == "N9")
    assert news["title"] == item.title and news["event_date"] == "2026-08-01"
    assert not payload["citations"]["N9"]["eligible_for_prose"]
    assert payload["citations"]["N9"]["news"]["publisher"] == "Independent publisher"


def test_original_official_news_fetched_with_provenance(research):
    class Client:
        def get(self, url, **kwargs):
            return SimpleNamespace(
                content=b"<p>Company announces quarterly earnings results. Revenue increased primarily due to demand for subscription services across its customer base.</p>",
                media_type="text/html",
                fetched_at=NOW.isoformat(),
                sha256="d" * 64,
                cached=False,
            )

    item = NewsItem(
        "Original",
        "Earnings",
        "Company",
        "https://www.microsoft.com/en-us/Investor/earnings",
        "2026-08-03",
    )
    enrich_news(Client(), [item], research.documents)
    assert item.content and item.retrieved_at == NOW.isoformat() and item.sha256 == "d" * 64
    assert item.content[0]["quote"].startswith("Company announces")


@pytest.mark.parametrize(
    "field,value",
    [
        ("metric", "net_income"),
        ("period_end", "2021-06-30"),
        ("period_start", "2021-01-01"),
        ("currency", "KZT"),
        ("value", "999"),
        ("source_urls", ["https://unrelated.example"]),
    ],
)
def test_quantitative_claim_cannot_reassign_correct_number(research, field, value):
    evidence = build_model_evidence(research)
    original = next(
        v for v in evidence["quantitative_evidence"].values() if v["metric"] == "revenue"
    )
    assert validate_narrative({"quantitative_claims": [original]}, evidence)
    claim = {**original, field: value}
    with pytest.raises(ValueError, match="metric, period, currency"):
        validate_narrative({"quantitative_claims": [claim]}, evidence)


def test_unrelated_but_valid_citation_rejected_for_number(research):
    evidence = build_model_evidence(research)
    original = next(
        v for v in evidence["quantitative_evidence"].values() if v["metric"] == "revenue"
    )
    assert "D2:B2" in evidence["citations"]
    claim = {**original, "citation_ids": ["D2:B2"]}
    with pytest.raises(ValueError, match="source"):
        validate_narrative({"quantitative_claims": [claim]}, evidence)


def test_prose_support_must_belong_to_cited_source(research):
    evidence = build_model_evidence(research)
    text = evidence["citations"]["D2:B2"]["quote"]
    p = {
        "kind": "interpretation",
        "text": "Review comparability before interpreting the trend.",
        "citation_ids": ["D2:B2"],
        "support": [{"citation_id": "D2:B2", "quote": text}],
    }
    assert validate_narrative({"paragraphs": [p]}, evidence)
    wrong = deepcopy(p)
    wrong["citation_ids"] = ["E3:B1"]
    wrong["support"][0]["citation_id"] = "E3:B1"
    with pytest.raises(ValueError, match="absent"):
        validate_narrative({"paragraphs": [wrong]}, evidence)
    wrong = {**p, "text": "Revenue 100 in 2021"}
    with pytest.raises(ValueError, match="numerical"):
        validate_narrative({"paragraphs": [wrong]}, evidence)


def test_management_causal_paraphrase_not_claimed_verified(research):
    evidence = build_model_evidence(research)
    text = evidence["citations"]["D2:B2"]["quote"]
    p = {
        "kind": "management explanation",
        "text": text,
        "citation_ids": ["D2:B2"],
        "support": [{"citation_id": "D2:B2", "quote": text}],
    }
    assert validate_narrative({"paragraphs": [p]}, evidence)
    p["text"] = "Management confirms profits increased because of an acquisition."
    with pytest.raises(ValueError, match="verbatim"):
        validate_narrative({"paragraphs": [p]}, evidence)


def test_failed_run_ui_has_no_success_banner(monkeypatch, research):
    research.documents = []
    research.dataset = None
    research.news = []
    research.stages = {"Company resolution": "failed"}
    monkeypatch.setattr("finsight.research.ui.find_companies", lambda *args: [research.company])
    monkeypatch.setattr("finsight.research.ui.run_research", lambda *args, **kwargs: research)
    monkeypatch.setenv("SEC_USER_AGENT", "FinSight tests contact@example.org")
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.text_input[0].set_value("Fixture")
    app.button[0].click().run()
    next(b for b in app.button if b.label == "Research selected company").click().run()
    assert not app.exception
    assert any("Research failed" in e.value for e in app.error)
    assert not app.success
    assert app.status[0].state == "error"


def test_release_preferred_over_same_day_cover_and_foreign_interim_detected(research):
    earnings = research.documents[-1]
    cover = replace(earnings, id="Cover", kind="current report", title="8-K — 2026-08-02")
    research.documents.insert(1, cover)
    assert recent_evidence(research.documents)[1]["document"].id == "E3"
    foreign = replace(
        research.documents[2],
        id="Foreign",
        kind="earnings/event exhibit",
        title="Exhibit to 6-K",
        published="2026-08-12",
        period="2026-08-12",
        passages=[
            Passage("HTML text block 1", "Interim Condensed Consolidated"),
            Passage("HTML text block 2", "Financial Information"),
            Passage(
                "HTML text block 3", "For the three and six months ended 30 June 2026 (Unaudited)"
            ),
            Passage(
                "HTML text block 4",
                "Revenue increased primarily due to subscription demand in the three and six months ended 30 June 2026, according to management.",
            ),
            Passage("HTML text block 5", "Acquisition of subsidiary with NCI"),
        ],
    )
    research.documents.append(foreign)
    selected = recent_evidence(research.documents)[0]
    assert selected["document"].id == "Foreign"
    news = official_news([foreign], research.news_start, research.news_end)
    assert news[0].title.startswith("Interim financial disclosure")
    assert "Acquisition" not in news[0].title


def test_period_cues_distinguish_quarter_and_ytd_without_dividend_frequency():
    from finsight.research.evidence import period_basis

    assert "quarterly" in period_basis("three and six months ended June 30, 2026")
    assert "year-to-date" in period_basis("three and six months ended June 30, 2026")
    assert "quarterly" in period_basis("Kaspi.kz 2Q & 1H 2026 financial results")
    assert "year-to-date" in period_basis("quarter and first half ended June 30, 2026")
    assert "not established" in period_basis("The board increased the quarterly dividend.")


def test_paywall_interstitial_is_not_read_article(research):
    from finsight.research.documents import read_document

    doc = research.documents[-1]

    class Client:
        def get(self, *args, **kwargs):
            return SimpleNamespace(
                content=b"<p>Subscribe to continue reading this article. Your subscription gives access to company news, research and exclusive commentary.</p>",
                media_type="text/html",
                fetched_at=NOW.isoformat(),
                sha256="f" * 64,
                cached=False,
            )

    read_document(Client(), doc, refresh=True)
    assert doc.status == "inaccessible" and not doc.passages


def test_shared_recent_news_citation_preserves_disclosure_context(research):
    evidence = build_model_evidence(research)
    citation = evidence["citations"]["E3:B1"]
    assert citation["kind"] == "disclosure excerpt"
    assert citation["publication_date"] == "2026-08-02"
    assert citation["source_report_date"] == "2026-08-02"
    assert citation["quote"] == research.news[0].content[0]["quote"]


def test_explicit_past_event_date_has_its_own_source(research):
    doc = research.documents[-1]
    doc.published = "2026-09-10"
    doc.passages.append(
        Passage(
            "HTML text block 2",
            "The following resolutions were duly passed at its Extraordinary General Meeting on 09 September 2026: payment of a dividend was approved by shareholders.",
        )
    )
    items = official_news([doc], research.news_start, research.news_end)
    enrich_news(None, items, [doc])
    assert items[0].event_date == "2026-09-09"
    ref = items[0].event_date_source["citation_id"]
    assert any(c["citation_id"] == ref and "09 September" in c["quote"] for c in items[0].content)
    assert items[0].published != items[0].event_date


def test_one_financial_metric_does_not_establish_complete_coverage(research):
    research.dataset = research.dataset.model_copy(
        update={
            "selected_ids": tuple(
                f.id for f in research.dataset.selected if f.metric.value == "revenue"
            )
        }
    )
    result = assess(research)
    assert result["status"] == "partial"
    assert any("net_income" in m and "operating_cash_flow" in m for m in result["missing"])
