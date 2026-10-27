import json
import zipfile
from copy import deepcopy
from pathlib import Path

from finsight.research.models import from_snapshot
from finsight.research.presentation import display_fact, display_number
from finsight.research.report import build_report


def test_display_rounding_preserves_exact_records_and_small_signs():
    claim = {
        "metric": "net_margin",
        "value": "26.38871656820908366974998480",
        "unit": "percent",
        "currency": "KZT",
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
    }
    original = deepcopy(claim)
    assert "26.39%" in display_fact(claim)
    assert claim == original
    assert display_number("4046074000000", "KZT") == "4.05 trillion KZT"
    assert display_number("0.0001", "percent") == "<0.01%"
    assert display_number("-0.0001", "percent") == ">-0.01%"


def test_summary_is_before_complete_appendix_and_keeps_period_boundaries():
    root = Path(__file__).parents[1] / "docs/review-artifacts/2026-10-26-no-api"
    for ticker in ["AAPL", "MSFT", "KSPI"]:
        with zipfile.ZipFile(root / f"{ticker}-research.zip") as z:
            research = from_snapshot(json.loads(z.read("research-evidence.json")))
            old_citations = json.loads(z.read("citations.json"))
        report, citations = build_report(research)
        assert (
            report.index("## Opening summary")
            < report.index("## Evidence appendix")
            < report.index("## Key findings")
        )
        summary = report.split("## Opening summary")[1].split("## Evidence appendix")[0]
        for label in [
            "Business model",
            "Latest reported change",
            "Supported operating drivers",
            "Financial risks",
            "Separate annual calculations",
            "Missing evidence",
        ]:
            assert label in summary
        assert "do not explain a newer quarter" in summary
        if ticker == "AAPL":
            assert "quarterly revenue of $109.4 billion" in summary
            assert "Products gross margin" in summary
            assert "insufficient selected evidence" not in summary
        if ticker == "MSFT":
            assert "generic cautions" in summary
            assert "Private Securities Litigation Reform Act" not in summary
        assert "## Document register" in report and "## Citation register" in report
        assert citations == old_citations
