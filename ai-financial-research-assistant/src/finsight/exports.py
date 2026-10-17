"""Analyst-readable tables plus exact decimal CSVs; neutralise spreadsheet formulas."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from openpyxl import Workbook

from finsight.models import Calculation, Dataset


def scalar(value):
    if value is None:
        return ""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, default=str)
    return value


def safe_cell(value):
    text = str(scalar(value))
    # Decimal numeric fields are trusted numeric output; all text fields are untrusted.
    if not isinstance(value, (Decimal, int, float)) and text.lstrip().startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + text
    return text


def tables(dataset: Dataset, calculations: list[Calculation]) -> dict[str, list[dict]]:
    financials = [dict(f.model_dump(), fact_id=f.id) for f in dataset.selected]
    sources = [
        dict(f.model_dump(), fact_id=f.id, selected=f.id in dataset.selected_ids)
        for f in dataset.observations
    ]
    warnings = [w.model_dump() for w in dataset.warnings]
    warnings += [
        {
            "code": "CALCULATION_UNAVAILABLE",
            "message": c.warning,
            "period_end": c.period_end,
            "metric": c.metric,
        }
        for c in calculations
        if c.warning
    ]
    metadata = [
        {"key": k, "value": v}
        for k, v in {
            "application_version": "0.1.0",
            "company": dataset.company,
            "cik": dataset.cik,
            "origin": dataset.origin,
            "accounting_basis": dataset.accounting_basis,
            "financial_group": dataset.financial_group,
            "fetched_at": dataset.fetched_at,
            "policy": dataset.policy,
            "source_hashes": dataset.source_hashes,
            "fcf_definition": (
                "Suppressed for financial groups; CFO is not distributable cash."
                if dataset.financial_group
                else "Operating cash flow less purchases of property, plant and equipment; not FCFF."
            ),
            "precision": "Exact decimal strings retained in CSV/XLSX. Parse as numeric for further calculations.",
            "text_safety": "Formula-like text is prefixed with an apostrophe in spreadsheet exports.",
            "limitations": "Limited concepts/companies; no point-in-time guarantee, FX conversion, cause inference or investment recommendations.",
        }.items()
    ]
    return {
        "financials": financials,
        "calculations": [c.model_dump() for c in calculations],
        "sources": sources,
        "warnings": warnings,
        "metadata": metadata,
    }


def csv_bytes(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    if rows:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: safe_cell(v) for k, v in row.items()} for row in rows)
    return stream.getvalue().encode("utf-8-sig")


def csv_bundle(dataset: Dataset, calculations: list[Calculation]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, rows in tables(dataset, calculations).items():
            archive.writestr(f"{name}.csv", csv_bytes(rows))
    return output.getvalue()


def excel_bytes(dataset: Dataset, calculations: list[Calculation]) -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name, rows in tables(dataset, calculations).items():
        sheet = workbook.create_sheet(name)
        if not rows:
            continue
        sheet.append(list(rows[0]))
        for row in rows:
            sheet.append([safe_cell(v) for v in row.values()])
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = 24
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()
