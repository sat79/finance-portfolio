"""Browser acceptance against explicit historical replay harness (see research-validation.md)."""

import io
import os
import re
import zipfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get("FINSIGHT_CHROMIUM", "/usr/bin/chromium"),
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(os.environ.get("FINSIGHT_BASE_URL", "http://127.0.0.1:8507"))
    page.get_by_text("TEST REPLAY ONLY", exact=False).wait_for()
    for name, ticker, legal_name in [
        ("Apple", "AAPL", "Apple Inc."),
        ("Microsoft", "MSFT", "MICROSOFT CORP"),
        ("Kaspi.kz", "KSPI", "Joint Stock Co Kaspi.kz"),
        ("NVIDIA", "NVDA", "NVIDIA CORP"),
    ]:
        page.get_by_label("Company name or ticker").fill(name)
        page.get_by_role("button", name="Find company", exact=True).click()
        if ticker == "AAPL":
            page.get_by_text("Select a legal entity before starting research.").wait_for()
            assert page.get_by_role("button", name="Research selected company").count() == 0
            page.get_by_role("combobox").click()
            page.get_by_role("option").filter(has_text="AAPL").click()
        expect(page.get_by_role("combobox")).to_have_value(re.compile(ticker))
        page.get_by_role("button", name="Research selected company").click()
        page.get_by_role("heading", name=f"Research report: {legal_name}", exact=True).wait_for()
        page.get_by_role("heading", name="Research conclusion", exact=False).wait_for()
        assert page.get_by_text("TEST REPLAY: dated saved evidence", exact=False).count() > 0
        page.get_by_role("tab", name="Download research", exact=True).click()
        with page.expect_download() as pending:
            page.get_by_role("button", name="Download research evidence bundle", exact=True).click()
        payload = Path(pending.value.path()).read_bytes()
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            report = archive.read("research-report.md").decode()
            assert ticker in report and "TEST REPLAY" in report
            assert "citations.json" in archive.namelist()
            assert "model-evidence.json" in archive.namelist()
            assert "Research outcome: PARTIAL" in report
            assert "Latest interim and earnings evidence alongside the annual baseline" in report
            assert "Discovery only" in report
            assert ("financial-analysis.xlsx" in archive.namelist()) == (ticker != "NVDA")
        page.get_by_role("tab", name="Company research report", exact=True).click()
        if ticker == "KSPI":
            assert "CFO is not distributable cash" in report
            page.screenshot(path="/tmp/finsight-research-kspi.png", full_page=False)
        print(
            f"PASS historical browser replay: {ticker} report, citations, bundle, financial coverage",
            flush=True,
        )
    page.get_by_label("Company name or ticker").fill("NonexistentPrivateExampleZZZ")
    page.get_by_role("button", name="Find company", exact=True).click()
    page.get_by_text("No matching US-listed entity found", exact=False).wait_for()
    assert page.get_by_role("heading", name="Research report:", exact=False).count() == 0
    print("PASS ambiguous confirmation, unsupported search and stale report reset")
    browser.close()
