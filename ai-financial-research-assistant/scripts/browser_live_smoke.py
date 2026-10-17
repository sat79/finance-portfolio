import csv
import io
import json
import os
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

base = Path(__file__).resolve().parents[1]
expected = json.loads((base / "tests/fixtures/reconciled_companies.json").read_text())
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get("FINSIGHT_CHROMIUM", "/usr/bin/chromium"),
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.goto(os.environ.get("FINSIGHT_BASE_URL", "http://127.0.0.1:8502"))
    page.get_by_role("button", name="Fetch SEC annual data").wait_for()
    for company in expected:
        labels = {"KSPI": "Kaspi.kz", "AAPL": "Apple Inc.", "MSFT": "Microsoft Corporation"}
        page.get_by_role("combobox").click()
        page.get_by_text(f"{company['ticker']} — {labels[company['ticker']]}", exact=True).click()
        page.get_by_role("button", name="Fetch SEC annual data").click()
        page.get_by_role("heading", name=company["dataset"]["company"], exact=True).wait_for(
            timeout=60000
        )
        page.get_by_role("tab", name="Ratios & trends").click()
        page.get_by_role("heading", name="Calculated metrics").wait_for()
        page.get_by_role("tab", name="Sources & warnings").click()
        page.get_by_text("Open SEC filing index", exact=True).first.wait_for(timeout=30000)
        # Screenshots and uploads are not persisted by this check.
        page.get_by_role("tab", name="Export", exact=True).click()
        with page.expect_download() as download:
            page.get_by_role("button", name="Download CSV bundle").click()
        archive = zipfile.ZipFile(download.value.path())
        rows = list(csv.DictReader(io.StringIO(archive.read("financials.csv").decode("utf-8-sig"))))
        checks = 0
        for year, metrics in company["expected"].items():
            for metric, value in metrics.items():
                row = next(r for r in rows if r["fiscal_year"] == year and r["metric"] == metric)
                assert row["value"] == value, (company["ticker"], year, metric, row["value"], value)
                assert row["status"] == "reported" and row["source_url"].startswith(
                    "https://www.sec.gov/Archives/"
                )
                checks += 1
        print(
            f"PASS: {company['ticker']} live/cache browser load, ratios, sources, CSV download; {checks} exported financial facts match independent filing reconciliation."
        )
    browser.close()
