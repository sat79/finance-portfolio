"""Synthetic behavior regressions; the real-company benchmark is evaluated separately."""

from datetime import date, datetime, timezone

from finsight.research.evidence import recent_evidence
from finsight.research.findings import key_findings
from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import Company, Document, NewsItem, Passage, Research
from finsight.research.report import build_report
from finsight.research.selection import MAX_CONTEXT, MAX_PRIMARY, select_passages, similar


def document(texts, *, interim=False):
    return Document(
        "D1",
        "10-Q — 2026-08-01" if interim else "Earnings release",
        "interim/amendment" if interim else "earnings/event exhibit",
        "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/results.htm",
        "2026-08-01",
        "2026-06-30",
        status="read",
        sha256="a" * 64,
        retrieved_at="2026-10-24T01:00:00+00:00",
        passages=[Passage(f"HTML text block {i}", t) for i, t in enumerate(texts, 1)],
    )


def research(doc):
    return Research(
        Company("Example Company", "EX", "Test", "0000000001"),
        datetime.now(timezone.utc),
        date(2026, 7, 1),
        date(2026, 10, 24),
        documents=[doc],
    )


def test_short_results_keep_nearby_period_units_and_accounting_basis():
    doc = document(
        [
            "Financial results for the quarter ended June 30, 2026.",
            "2Q 2026 Highlights",
            "(In millions, except per-share amounts)",
            "Revenue was 900 and increased 18% (up 17% in constant currency).",
            "Net income was 358, up 31% on a GAAP basis, and 353, up 22% on a non-GAAP basis.",
        ]
    )
    selected = recent_evidence([doc])[0]
    texts = [p.text for p in selected["passages"]]
    assert all(p.text in texts for p in doc.passages)
    record = next(r for r in selected["records"] if r["index"] == 3)
    assert 1 in record["context_indices"] and 2 in record["context_indices"]
    r = research(doc)
    report, citations = build_report(r)
    payload = build_model_evidence(r)
    assert "## Key findings" in report and report.index("## Key findings") < report.index(
        "## What the business"
    )
    for key in ["D1:B4", "D1:B5"]:
        assert payload["citations"][key]["quote"] == citations[key]["quote"]
        assert key in {p["citation_id"] for p in payload["recent_disclosures"][0]["passages"]}
    assert not payload["quantitative_evidence"]  # No quarterly observations invented from prose.


def test_credit_stock_does_not_inherit_year_to_date_flow_as_period():
    doc = document(
        [
            "Interim financial results",
            "During the six months ended June 30, 2026, USD 80 million of restructured loans were collected.",
            "As at December 31, 2025 and June 30, 2026, restructured loans in Stage 3 had gross carrying amounts of USD 145 million and USD 178 million, respectively.",
        ],
        interim=True,
    )
    record = next(r for r in select_passages(doc) if r["topic"] == "credit_risk")
    assert record["index"] == 2 and 1 not in record["context_indices"]
    r = research(doc)
    finding = next(f for f in key_findings(r) if f["topic"] == "credit_risk")
    assert "subset" in finding["question"] and "balance-sheet dates" in finding["question"]
    assert "gross carrying amounts" in finding["statements"][0]["text"]


def test_driver_paraphrases_are_deduplicated_with_original_locations():
    assert similar(
        "GMV increased 28% to 1300 million. TPV increased 18% to 2400 million.",
        "Across our platforms TPV reached 2400 million with 18% growth, while GMV reached 1300 million after 28% growth.",
    )
    first = "Digital take rate increased 160 bps to 16.1%. Constant currency revenue increased 35% to USD394 million, with services up 49% and profit USD820 million."
    repeat = "Our monetization improved, with revenue of USD394 million up 35% at constant currency, services growth of 49%, take rate up 160 bps to 16.1% and profit of USD820 million."
    doc = document(
        [
            "Quarterly financial results",
            "2Q 2026 Highlights",
            first,
            repeat,
            "Commerce remained the main growth driver. GMV increased 28% to USD1.3 billion and purchases increased 33% year-over-year.",
        ]
    )
    records = select_passages(doc)
    assert sum(r["index"] in {2, 3} for r in records) == 1
    assert any(r["index"] == 4 for r in records)
    assert len(records) <= MAX_PRIMARY and all(
        len(r["context_indices"]) <= MAX_CONTEXT for r in records
    )


def test_no_forced_findings_from_boilerplate_or_headings():
    doc = document(
        [
            "2Q 2026 Financial results",
            "Financial results conference call and webcast will take place on August 1, 2026. All forward-looking statements involve substantial risk.",
        ]
    )
    r = research(doc)
    assert key_findings(r) == []
    assert "no finding was manufactured" in build_report(r)[0]


def test_split_explanations_are_exact_source_spans_not_generated_causes():
    text = "Company revenue increased 15% to USD1.1 billion. Net income was stable at USD259 million, even with higher funding costs."
    r = research(document(["Quarterly financial results", "2Q 2026 Highlights", text]))
    f = key_findings(r)[0]
    assert {s["kind"] for s in f["statements"]} == {"reported fact", "management explanation"}
    assert all(s["text"] in text for s in f["statements"])
    assert "does not quantify" in f["question"]
    driver = "Commerce remained our main growth driver. GMV increased 28% to USD1.3 billion and purchases increased 33% year-over-year."
    f = key_findings(research(document(["Quarterly financial results", driver])))[0]
    assert f["statements"][0]["kind"] == "management explanation"
    assert f["statements"][1]["kind"] == "reported fact"


def test_shorter_news_excerpt_cannot_overwrite_selected_full_quote():
    text = (
        "Quarterly financial results: company revenue increased 15% to USD1.1 billion, with net income of USD259 million. "
        + "The scope includes the consolidated operations and all reported comparative periods. "
        * 13
    )
    assert 1000 < len(text) <= 1600
    doc = document([text])
    r = research(doc)
    r.news = [
        NewsItem(
            "N1",
            "Quarterly results",
            "Company",
            doc.url,
            doc.published,
            document_id=doc.id,
            content=[
                {
                    "citation_id": "D1:B1",
                    "quote": text[:1000],
                    "url": doc.url,
                    "locator": "HTML text block 1",
                    "period_basis": "quarterly",
                }
            ],
        )
    ]
    _, citations = build_report(r)
    assert citations["D1:B1"]["quote"] == text
    assert build_model_evidence(r)["citations"]["D1:B1"]["quote"] == text


def test_warning_interning_and_key_calculations_preserve_inputs(dataset):
    from test_research import report_fixture

    from finsight.models import Warning

    r = report_fixture(dataset)
    r.dataset = r.dataset.model_copy(
        update={
            "warnings": (
                *r.dataset.warnings,
                Warning(
                    code="TEST_SCOPE",
                    message="Reported scope differs; do not call this organic growth.",
                ),
            )
        }
    )
    payload = build_model_evidence(r)
    assert (
        "TEST_SCOPE: Reported scope differs; do not call this organic growth."
        in payload["warning_registry"].values()
    )
    for row in payload["calculations"] + payload["selected_financial_observations"]:
        assert all(key in payload["warning_registry"] for key in row["review_warning_ids"])
    for f in payload["key_findings"]:
        for key in f["calculation_ids"]:
            claim = payload["quantitative_evidence"][key]
            assert all(c in payload["citations"] for c in claim["citation_ids"])


def test_equivalent_undated_supplements_keep_aliases_without_repeated_evidence():
    from dataclasses import replace

    doc = document(
        [
            "Quarterly financial results. Revenue was USD900 million and net income was USD200 million."
        ]
    )
    first = replace(doc, id="IR2", kind="IR linked document", published="Not established")
    second = replace(first, id="IR3", url=doc.url.replace("results", "alternate"))
    selections = recent_evidence([doc, first, second])
    assert len(selections) == 2 and selections[1]["duplicate_document_ids"] == ["IR3"]
    assert selections[1]["passages"] and not selections[1]["latest_eligible"]


def test_bundle_retains_all_cited_article_text_and_original_block_numbers():
    import io
    import json
    import zipfile
    from dataclasses import replace

    from finsight.research.report import report_bundle

    doc = replace(
        document(
            [
                "Unselected original article text.",
                "Original article discusses management and market developments in sufficient detail for a cited passage.",
            ]
        ),
        kind="news original",
    )
    r = research(doc)
    r.news = [
        NewsItem(
            "N1",
            "Original article",
            "Publisher",
            doc.url,
            doc.published,
            document_id=doc.id,
            content=[
                {
                    "citation_id": "D1:B2",
                    "quote": doc.passages[1].text,
                    "url": doc.url,
                    "locator": doc.passages[1].locator,
                    "period_basis": "not established",
                }
            ],
        )
    ]
    with zipfile.ZipFile(io.BytesIO(report_bundle(r))) as archive:
        snapshot = json.loads(archive.read("research-evidence.json"))
        citations = json.loads(archive.read("citations.json"))
    assert snapshot["documents"][0]["passages"][0]["text"] == ""
    assert snapshot["documents"][0]["passages"][1]["text"] == citations["D1:B2"]["quote"]
    assert doc.passages[0].text == "Unselected original article text."
