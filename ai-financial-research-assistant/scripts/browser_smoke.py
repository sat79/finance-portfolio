import os
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get("FINSIGHT_CHROMIUM", "/usr/bin/chromium"),
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(os.environ.get("FINSIGHT_BASE_URL", "http://127.0.0.1:8501"))
    page.get_by_text("No analysis loaded.", exact=False).wait_for()
    page.get_by_text("Synthetic example", exact=True).click()
    page.get_by_role("button", name="Load fictional example").click()
    page.get_by_role("heading", name="Fixture Manufacturing (fictional)", exact=True).wait_for()
    page.get_by_role("tab", name="Ratios & trends").click()
    page.get_by_text("FY2023 (2023-06-30): revenue increased by 20.00%.", exact=True).wait_for()
    # No uploads or screenshots are persisted by this smoke check.
    page.get_by_role("tab", name="Export", exact=True).click()
    with page.expect_download() as download:
        page.get_by_role("button", name="Download CSV bundle").click()
    assert download.value.suggested_filename == "finsight-analysis.zip"
    with page.expect_download() as download:
        page.get_by_role("button", name="Download Excel workbook").click()
    assert download.value.suggested_filename == "finsight-analysis.xlsx"
    page.get_by_text("Upload CSV", exact=True).click()
    page.locator("input[type=file]").set_input_files(
        str(root / "data/examples/invalid_negative_capex.csv")
    )
    page.get_by_text("Row 2: capex must be a positive outflow", exact=False).wait_for()
    assert page.get_by_role("button", name="Analyse validated CSV").count() == 0
    page.locator("input[type=file]").set_input_files(
        str(root / "data/examples/valid_synthetic.csv")
    )
    page.get_by_role("heading", name="Import preview", exact=False).wait_for()
    page.get_by_role("button", name="Analyse validated CSV").click()
    page.get_by_text("User-provided data. Source references", exact=False).wait_for()
    page.get_by_role("tab", name="Sources & warnings").click()
    page.get_by_role("heading", name="Trace each observation").wait_for()
    # Source inspection completed.
    page.get_by_text("SEC company", exact=True).click()
    page.get_by_text("No analysis loaded.", exact=False).wait_for()
    page.get_by_role("button", name="Fetch SEC annual data").click()
    page.get_by_text("Set SEC_USER_AGENT locally", exact=False).wait_for()
    assert (
        page.get_by_role("heading", name="Fixture Manufacturing (fictional)", exact=True).count()
        == 0
    )
    print(
        "PASS: browser example, hand-checked ratios, CSV/XLSX downloads, invalid/valid uploads, preview, sources, mode reset and SEC config error."
    )
    browser.close()
