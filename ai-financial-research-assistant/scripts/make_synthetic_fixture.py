"""Reproduce the fictional parser fixture; NOT real-company financial evidence."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
concepts = {
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "operating_profit": "OperatingIncomeLoss",
    "net_income": "NetIncomeLoss",
    "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "cash": "CashAndCashEquivalentsAtCarryingValue",
    "assets": "Assets",
    "liabilities": "Liabilities",
}
# Small hand-checkable numbers, whole USD. Negative earnings and CFO are intentional.
values = {
    2022: [1000, 100, 80, 150, 50, 100, 2000, 900],
    2023: [1200, 96, -24, -20, 30, 80, 2100, 1000],
    2024: [1500, 180, 120, 220, 70, 130, 2300, 1100],
}
facts = {"cik": 1, "entityName": "Fixture Manufacturing (fictional)", "facts": {"us-gaap": {}}}
recent = {key: [] for key in ["accessionNumber", "form", "reportDate", "filingDate"]}
rows = []
for year, amounts in values.items():
    accession = f"0000000001-{str(year)[2:]}-000001"
    for key, value in zip(recent, [accession, "10-K", f"{year}-06-30", f"{year}-08-01"]):
        recent[key].append(value)
    for (metric, concept), amount in zip(concepts.items(), amounts):
        row = {
            "end": f"{year}-06-30",
            "val": amount,
            "accn": accession,
            "fy": year,
            "fp": "FY",
            "form": "10-K",
            "filed": f"{year}-08-01",
        }
        if metric not in {"cash", "assets", "liabilities"}:
            row["start"] = f"{year - 1}-07-01"
        facts["facts"]["us-gaap"].setdefault(concept, {"units": {"USD": []}})["units"][
            "USD"
        ].append(row)
        rows.append(
            [
                "1",
                facts["entityName"],
                "0000000001",
                year,
                f"{year - 1}-07-01",
                f"{year}-06-30",
                "USD",
                "USD",
                metric,
                amount,
                "Fictional teaching example; no real filing",
            ]
        )
(ROOT / "tests/fixtures/synthetic_companyfacts.json").write_text(json.dumps(facts, indent=2) + "\n")
(ROOT / "tests/fixtures/synthetic_submissions.json").write_text(
    json.dumps({"cik": "0000000001", "filings": {"recent": recent}}, indent=2) + "\n"
)
header = [
    "schema_version",
    "company",
    "cik",
    "fiscal_year",
    "period_start",
    "period_end",
    "currency",
    "unit",
    "metric",
    "value",
    "source_reference",
]
for name, body in [
    ("valid_synthetic.csv", rows),
    ("invalid_negative_capex.csv", [rows[4][:9] + [-50] + rows[4][10:]]),
]:
    with (ROOT / "data/examples" / name).open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(body)
