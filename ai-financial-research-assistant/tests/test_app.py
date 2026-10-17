from pathlib import Path

from streamlit.testing.v1 import AppTest

from finsight.sec import SECError

APP = Path(__file__).resolve().parents[1] / "app/main.py"


def test_user_can_load_example_review_calculations_and_export():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert any("No analysis loaded" in i.value for i in app.info)
    app.radio[0].set_value("Synthetic example").run()
    app.button[0].click().run()
    assert not app.exception
    assert app.header[0].value == "Fixture Manufacturing (fictional)"
    assert [tab.label for tab in app.tabs] == [
        "Financial statements",
        "Ratios & trends",
        "Sources & warnings",
        "Export",
    ]
    assert len(app.dataframe) == 4
    assert any("20.00%" in m.value for m in app.markdown)
    assert len(app.get("download_button")) == 2
    assert any("fictional" in w.value.lower() for w in app.warning)
    app.radio[0].set_value("SEC company").run()
    assert "dataset" not in app.session_state
    assert not app.exception


def test_api_failure_visible_and_no_fallback(monkeypatch):
    def fail(*args, **kwargs):
        raise SECError("SEC HTTP 403: blocked during test")

    monkeypatch.setattr("finsight.sec.SECClient.load", fail)
    monkeypatch.setenv("SEC_USER_AGENT", "FinSight tests contact@example.org")
    app = AppTest.from_file(str(APP)).run()
    app.button[0].click().run()
    assert not app.exception
    assert "403" in app.error[0].value
    assert "dataset" not in app.session_state


def test_csv_mode_exposes_template_and_preview_workflow():
    app = AppTest.from_file(str(APP)).run()
    app.radio[0].set_value("Upload CSV").run()
    assert not app.exception
    assert len(app.get("file_uploader")) == 1
    assert len(app.get("download_button")) == 1


def test_kspi_default_and_financial_group_explanations(monkeypatch):
    import json
    from datetime import datetime, timezone

    from finsight.selection import select_annual

    fixture = APP.parents[1] / "tests/fixtures"
    data = select_annual(
        json.loads((fixture / "kspi_companyfacts.json").read_text()),
        json.loads((fixture / "kspi_submissions.json").read_text()),
        cik="0001985487",
        origin="sec_cache",
        fetched_at=datetime.now(timezone.utc),
    )
    monkeypatch.setenv("SEC_USER_AGENT", "FinSight tests contact@example.org")
    monkeypatch.setattr("finsight.sec.SECClient.load", lambda *args, **kwargs: data)
    app = AppTest.from_file(str(APP)).run()
    assert app.selectbox[0].value == "KSPI"
    app.button[0].click().run()
    assert not app.exception
    assert app.header[0].value == "Joint Stock Company Kaspi.kz"
    assert any("after customer rewards" in i.value for i in app.info)
    assert any("distributable cash" in w.value for w in app.warning)


def test_kspi_csv_does_not_claim_verified_ifrs_revenue_basis():
    from finsight.csv_import import import_csv

    content = (APP.parents[1] / "data/examples/valid_synthetic.csv").read_bytes()
    content = content.replace(b"0000000001", b"0001985487")
    data = import_csv(content)
    assert data.financial_group
    app = AppTest.from_file(str(APP)).run()
    app.session_state["dataset"] = data
    app.run()
    assert not app.exception
    assert not any("KSPI revenue is consolidated IFRS" in i.value for i in app.info)
    assert any("revenue definition" in w.value for w in app.warning)
    assert (
        "Consolidated IFRS revenue (after rewards)" not in app.dataframe[0].value["Metric"].tolist()
    )
