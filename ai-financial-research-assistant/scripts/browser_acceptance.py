"""Fresh production-app acceptance: real sources, no replay or workflow replacements.

Start app/main.py with a new FINSIGHT_CACHE_DIR, SEC_USER_AGENT and FINSIGHT_ENABLE_MODEL=0.
Requires an externally installed Playwright/Chromium; it is not an app dependency.
"""

import io
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

output = Path(os.environ.get("FINSIGHT_ACCEPTANCE_OUTPUT", "/tmp/finsight-browser-acceptance"))
output.mkdir(parents=True, exist_ok=True)
rows = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get("FINSIGHT_CHROMIUM", "/usr/bin/chromium"),
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.set_default_timeout(180000)
    page.goto(os.environ.get("FINSIGHT_BASE_URL", "http://127.0.0.1:8512"))
    for name, ticker in [("Apple", "AAPL"), ("Microsoft", "MSFT"), ("Kaspi.kz", "KSPI")]:
        attempted = datetime.now(timezone.utc).isoformat()
        print(f"START production journey: {ticker}", flush=True)
        page.get_by_label("Company name or ticker").fill(name)
        page.get_by_role("button", name="Find company", exact=True).click()
        if ticker == "AAPL":
            page.get_by_text("Select a legal entity before starting research.").wait_for()
            assert page.get_by_role("button", name="Research selected company").count() == 0
            page.get_by_role("combobox").fill("AAPL")
            page.get_by_role("combobox").press("ArrowDown")
            page.get_by_role("option").filter(has_text="AAPL").click()
        expect(page.get_by_role("combobox")).to_have_value(re.compile(ticker))
        expect(page.get_by_role("heading", name="Research report:", exact=False)).to_have_count(0)
        expect(
            page.get_by_role("button", name="Download research evidence bundle", exact=True)
        ).to_have_count(0)
        print(f"Confirmed entity: {ticker}", flush=True)
        refresh = page.get_by_label("Refresh evidence from sources (otherwise reuse dated cache)")
        if not refresh.is_checked():
            refresh.press("Space")
        expect(refresh).to_be_checked()
        page.get_by_role("button", name="Research selected company").click()
        page.get_by_role("heading", name="Research report:", exact=False).wait_for()
        page.get_by_role("heading", name="Research conclusion", exact=False).wait_for()
        assert "TEST REPLAY" not in page.inner_text("body")
        expect(page.get_by_text("Table analytical evidence:", exact=False).first).to_be_visible()
        page.get_by_role(
            "heading", name="Research report:", exact=False
        ).scroll_into_view_if_needed()
        page.screenshot(path=str(output / f"{ticker}-coverage.png"))
        assert page.locator('a[href^="https://www.sec.gov/Archives/"]').count() > 0
        page.get_by_role("heading", name="Key findings", exact=True).scroll_into_view_if_needed()
        page.screenshot(path=str(output / f"{ticker}-report.png"))
        page.get_by_role(
            "heading", name="Structured financial table evidence", exact=True
        ).first.scroll_into_view_if_needed()
        page.screenshot(path=str(output / f"{ticker}-tables.png"))
        page.get_by_role("tab", name="Evidence & coverage", exact=True).click()
        page.get_by_text("Inspect citation register", exact=True).click()
        expect(page.locator('[data-testid="stJson"]').last).to_be_visible(timeout=30000)
        page.screenshot(path=str(output / f"{ticker}-citations.png"))
        page.get_by_role("tab", name="Download research", exact=True).click()
        with page.expect_download() as pending:
            page.get_by_role("button", name="Download research report (.md)", exact=True).click()
        markdown = Path(pending.value.path()).read_bytes()
        (output / f"{ticker}-report.md").write_bytes(markdown)
        with page.expect_download() as pending:
            page.get_by_role(
                "button", name="Download compact evidence for manual ChatGPT use", exact=True
            ).click()
        manual = Path(pending.value.path()).read_bytes()
        (output / f"{ticker}-manual-synthesis.zip").write_bytes(manual)
        with zipfile.ZipFile(io.BytesIO(manual)) as pack:
            compact = json.loads(pack.read("evidence.json"))
            assert compact["company"]["ticker"] == ticker
            assert "quantitative_claims" in pack.read("instructions.txt").decode()
            assert "does not import" in pack.read("README.md").decode()
        with page.expect_download() as pending:
            page.get_by_role("button", name="Download research evidence bundle", exact=True).click()
        payload = Path(pending.value.path()).read_bytes()
        (output / f"{ticker}-research.zip").write_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            report = archive.read("research-report.md").decode()
            assert report.encode() == markdown
            evidence = json.loads(archive.read("research-evidence.json"))
            citations = json.loads(archive.read("citations.json"))
            coverage = json.loads(archive.read("coverage.json"))
            model = json.loads(archive.read("model-evidence.json"))
            assert evidence["company"]["ticker"] == ticker and ticker in report
            assert compact["research_cutoff"] == model["research_cutoff"]
            assert compact["limitations"] == model["limitations"]
            assert all(
                v == model["quantitative_evidence"][k]
                for k, v in compact["quantitative_evidence"].items()
            )
            assert all(
                v["support_text"] == model["citations"][k]["support_text"]
                for k, v in compact["citations"].items()
            )
            assert evidence["model_usage"]["calls"] == 0
            assert "Latest interim and earnings evidence alongside the annual baseline" in report
            assert citations and model["recent_disclosures"]
            assert 3 <= len(model["key_findings"]) <= 5
            assert report.index("## Key findings") < report.index("## What the business")
            assert "financial-analysis.xlsx" in archive.namelist()
            table_ids = [k for d in model["recent_disclosures"] for k in d["table_citation_ids"]]
            assert table_ids
            assert all(model["citations"][k]["table"] == citations[k]["table"] for k in table_ids)
            assert all(not model["citations"][k]["eligible_for_prose"] for k in table_ids)
            successful = [a for a in evidence["access_attempts"] if a["status"] == "retrieved"]
            assert successful and all(a["cached"] is False for a in successful)
            assert "TEST REPLAY" not in report
            assert all(
                key in coverage for key in ["official_documents", "financial", "independent_news"]
            )
            assert coverage["independent_news"]["label"] in report
            assert coverage["tables"]["summary"] in report
            assert (
                coverage["status"] == "partial"
                if coverage["tables"]["status"] != "bounded"
                else True
            )
            for item in model["recent_disclosures"]:
                for passage in item["passages"]:
                    assert passage["citation_id"] in citations
            row = {
                "query": name,
                "ticker": ticker,
                "attempted_at": attempted,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "cutoff": evidence["cutoff"],
                "coverage": coverage,
                "fresh_source_retrievals": len(successful),
                "citations": len(citations),
                "document_count": len(evidence["documents"]),
                "steps": [
                    "name search",
                    "previous report and downloads cleared",
                    "entity confirmation",
                    "refresh source evidence",
                    "read report",
                    "inspect citation register",
                    "download and inspect bundle",
                    "download matching Markdown and API-free manual evidence pack",
                ],
                "model_calls": 0,
                "retrieval_seconds": evidence["seconds"],
                "source_failures": [
                    a for a in evidence["access_attempts"] if a["status"] != "retrieved"
                ],
                "key_findings": len(model["key_findings"]),
                "structured_table_records": len(table_ids),
            }
            rows.append(row)
            (output / "summary.json").write_text(json.dumps(rows, indent=2))
        print(f"PASS production browser journey: {ticker}", flush=True)
        page.get_by_role("tab", name="Company research report", exact=True).click()
    browser.close()
