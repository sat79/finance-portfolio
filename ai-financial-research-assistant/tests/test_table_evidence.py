import json
from dataclasses import replace

import pytest

from finsight.research.documents import extract, read_document
from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import Document
from finsight.research.narrative import validate_narrative
from finsight.research.report import build_report, report_bundle
from finsight.research.tables import MAX_EVIDENCE_BYTES, extract_tables
from finsight.research.transport import EvidenceResponse

CONTEXT = "<p>Example Group</p><p>Consolidated statements of income</p><p>(In millions)</p>"
HEAD = '<tr><th rowspan="2">Metric</th><th colspan="2">Three Months Ended</th><th colspan="2">Six Months Ended</th></tr><tr><th>June 30, 2026</th><th>June 30, 2025</th><th>June 30, 2026</th><th>June 30, 2025</th></tr>'
ROWS = '<tr><td colspan="5">Net sales by segment</td></tr><tr><td>Region East</td><td>20</td><td>18</td><td>38</td><td>32</td></tr><tr><td>Net income</td><td>(4)</td><td>3</td><td>5</td><td>6</td></tr>'


def parse(body):
    return extract_tables(body.encode(), "text/html")


def test_spans_preserve_dates_scope_units_and_original_cells():
    tables, _ = parse(CONTEXT + "<table>" + HEAD + ROWS + "</table>")
    table = tables[0]
    assert table["status"] == "structured"
    assert table["units"][0]["text"] == "(In millions)"
    region, income = table["rows"]
    assert region["section"]["text"] == "Net sales by segment"
    assert [v["value_cell"]["text"] for v in income["values"]] == ["(4)", "3", "5", "6"]
    first, _, third, _ = income["values"]
    assert [h["text"] for h in first["column_headers"]] == ["Three Months Ended", "June 30, 2026"]
    assert [h["text"] for h in third["column_headers"]] == ["Six Months Ended", "June 30, 2026"]
    assert first["value_cell"]["column"] == 2
    assert first["value_cell"]["row"] == 5 and first["value_cell"]["cell"] == 2
    assert first["value_cell"]["position"][0] == 1


@pytest.mark.parametrize(
    "body,reason",
    [
        (CONTEXT + "<table><tr><td>Revenue</td><td>100</td></tr></table>", "Column date/year"),
        ("<table>" + HEAD + ROWS + "</table>", "scale/unit"),
        (CONTEXT + '<table><tr><td colspan="0">Revenue</td><td>100</td></tr></table>', "Invalid"),
        (
            CONTEXT + '<table><tr><td colspan="41">Revenue</td><td>100</td></tr></table>',
            "oversized",
        ),
        (
            CONTEXT
            + "<table><tr><td>Revenue</td><td>100<table><tr><td>Nested</td></tr></table></td></tr></table>",
            "Nested",
        ),
        (CONTEXT + "<table><tr><td>Revenue</td><td>100</td></tr>", "Unclosed"),
    ],
)
def test_unsupported_or_ambiguous_tables_fail_closed(body, reason):
    tables, _ = parse(body)
    assert tables and tables[0]["status"] in {"unsupported", "partial"}
    notes = " ".join(tables[0]["notes"]) + " ".join(r["reason"] for r in tables[0]["rows"])
    assert reason in notes
    assert all(not r["values"] for r in tables[0]["rows"])


def test_does_not_invent_column_relationships_from_flat_numbers_or_shared_heading():
    assert parse(CONTEXT + "<p>Revenue 100 200 2025 2026</p>")[0] == []
    assert extract_tables(b"%PDF example", "application/pdf")[0] == []
    html = (
        CONTEXT
        + '<table><tr><td></td><td colspan="2">Three Months Ended June 30, 2026</td></tr><tr><td>Revenue</td><td>100</td><td>200</td></tr></table>'
    )
    tables, _ = parse(html)
    assert tables[0]["rows"][0]["status"] == "ambiguous"
    assert tables[0]["rows"][0]["values"] == []
    tables, _ = parse(
        CONTEXT
        + "<table><tr><td></td><td>Quarterly margin 2026</td></tr><tr><td>Revenue</td><td>100</td></tr></table>"
    )
    assert tables[0]["rows"][0]["status"] == "ambiguous"  # "margin" is not March.
    repeated = "<td>Three Months Ended June 30, 2026</td>" * 2
    tables, _ = parse(
        CONTEXT
        + "<table><tr><td></td>"
        + repeated
        + "</tr><tr><td>Revenue</td><td>100</td><td>200</td></tr></table>"
    )
    assert tables[0]["rows"][0]["values"] == []  # Separate cells still need distinct headings.


def test_column_oriented_segments_are_explicitly_unsupported():
    tables, notes = parse(
        "<p>Segment revenue reconciliation</p><table><tr><th>Year</th><th>East</th><th>West</th></tr>"
        "<tr><td>2025</td><td>100</td><td>200</td></tr></table>"
    )
    assert tables[0]["status"] == "unsupported"
    assert "column-oriented" in " ".join(notes)
    assert tables[0]["rows"] == []


def test_table_and_row_budgets_are_visible(monkeypatch):
    rows = "".join(f"<tr><td>Revenue segment {i}</td><td>100</td></tr>" for i in range(20))
    html = "".join(
        CONTEXT
        + "<table><tr><td></td><td>Three Months Ended June 30, 2026</td></tr>"
        + rows
        + "</table>"
        for _ in range(6)
    )
    tables, notes = parse(html)
    assert len(tables) == 4 and all(len(t["rows"]) == 12 for t in tables)
    assert all(t["omitted_candidate_rows"] == 8 for t in tables)
    assert "2 additional" in notes[0]
    assert sum(len(json.dumps(t).encode()) for t in tables) <= MAX_EVIDENCE_BYTES
    monkeypatch.setattr("finsight.research.tables.MAX_EVIDENCE_BYTES", 100)
    tables, notes = parse(html)
    assert tables == [] and any("evidence budget exceeded" in note for note in notes)


def test_report_model_bundle_share_tables_without_normalizing_facts(dataset):
    import io
    import zipfile

    from test_research import report_fixture

    r = report_fixture(dataset)
    before = build_model_evidence(r)["quantitative_evidence"]
    body = (
        "<p>Quarterly financial results for the quarter ended June 30, 2026. The company issued its consolidated quarterly financial results.</p>"
        + CONTEXT
        + "<table>"
        + HEAD
        + ROWS
        + "</table>"
    )

    class Client:
        def get(self, url, *, refresh):
            return EvidenceResponse(
                body.encode(), "text/html", "2026-10-25T10:00:00+00:00", "a" * 64, False
            )

    doc = Document(
        "E1",
        "Quarterly results",
        "earnings/event exhibit",
        "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/results.htm",
        "2026-08-01",
        "2026-06-30",
    )
    read_document(Client(), doc, refresh=True)
    original_passages, _, _ = extract(body.encode(), "text/html", doc.url)
    assert doc.passages == original_passages  # B-citation ordinals unchanged.
    r.documents.append(doc)
    report, citations = build_report(r)
    model = build_model_evidence(r)
    assert model["quantitative_evidence"] == before
    assert citations["E1:T1"]["table"] == model["citations"]["E1:T1"]["table"] == doc.tables[0]
    assert not model["citations"]["E1:T1"]["eligible_for_prose"]
    assert "Six Months Ended / June 30, 2025" in report
    with pytest.raises(ValueError):
        validate_narrative(
            {
                "paragraphs": [
                    {
                        "kind": "interpretation",
                        "text": "Profit improved.",
                        "citation_ids": ["E1:T1"],
                        "support": [
                            {
                                "citation_id": "E1:T1",
                                "quote": "Company profit improved substantially.",
                            }
                        ],
                    }
                ]
            },
            model,
        )
    with zipfile.ZipFile(io.BytesIO(report_bundle(r))) as archive:
        snapshot = json.loads(archive.read("research-evidence.json"))
        assert snapshot["documents"][-1]["tables"] == doc.tables
    old = replace(doc, tables=[], table_notes=[])
    r.documents[-1] = old
    assert "not reconstructed from flattened numbers" in build_report(r)[0]
