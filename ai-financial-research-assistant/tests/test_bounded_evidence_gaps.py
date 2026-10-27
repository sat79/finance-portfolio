import json
import zipfile
from pathlib import Path

from finsight.research.model_evidence import build_model_evidence, compact_synthesis_evidence
from finsight.research.models import from_snapshot
from finsight.research.publisher import guardian_article
from finsight.research.tables import extract_tables

ROOT = Path(__file__).parents[1] / "docs/review-artifacts"


def test_compact_retains_one_retrieved_original_article_without_discovery_claims():
    for ticker in ["AAPL", "MSFT", "KSPI"]:
        with zipfile.ZipFile(ROOT / f"2026-10-26-no-api/{ticker}-research.zip") as z:
            research = from_snapshot(json.loads(z.read("research-evidence.json")))
        full = build_model_evidence(research)
        compact = compact_synthesis_evidence(full)
        assert compact_synthesis_evidence(compact) == compact
        independent = [n for n in compact["news"] if guardian_article(n["url"])]
        assert len(independent) == (0 if ticker == "KSPI" else 1)
        assert len(compact["news"]) <= 3
        assert compact["coverage"] == {
            **full["coverage"],
            "tables": {k: v for k, v in full["coverage"]["tables"].items() if k != "documents"},
        }
        for n in compact["news"]:
            original = next(x for x in full["news"] if x["id"] == n["id"])
            for key in [
                "title",
                "publisher",
                "published",
                "event_date",
                "url",
                "access",
                "retrieved_at",
                "sha256",
            ]:
                assert n[key] == original[key]
            assert n["content"]
            for c in n["content"]:
                ref = compact["citations"][c["citation_id"]]
                assert ref["eligible_for_prose"] and ref["support_text"]
                assert ref["support_text"] == full["citations"][c["citation_id"]]["support_text"]
        assert all(c["eligible_for_prose"] for c in compact["citations"].values())


def test_segment_results_heading_priority_preserves_source_and_budget():
    base = "<p>{}</p><p>(In millions)</p><table><tr><td></td><td>Three Months Ended June 30, 2026</td></tr><tr><td>Revenue</td><td>100</td></tr></table>"
    titles = [
        "Comprehensive income statements",
        "Income statements",
        "Balance sheets",
        "Cash flows statements",
        "SEGMENT RESULTS",
    ]
    tables, notes = extract_tables("".join(base.format(t) for t in titles).encode(), "text/html")
    assert [t["table"] for t in tables] == [5, 4, 2, 3]
    assert tables[0]["rows"][0]["values"][0]["value_cell"]["text"] == "100"
    assert tables[0]["context"][0]["text"] == "SEGMENT RESULTS"
    assert any("ordinals: 1" in n for n in notes)
