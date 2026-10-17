"""Strict, small CSV imports. All uploaded values remain user-provided."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import datetime, timezone
from decimal import Decimal

from pydantic import ValidationError

from finsight.models import BASE_METRICS, INSTANT_METRICS, Dataset, Fact, Metric, Period, Warning

MAX_CSV_BYTES = 1024 * 1024
MAX_ROWS = 1000
COLUMNS = (
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
)
NUMBER = re.compile(r"^-?(?:0|[1-9]\d{0,19})(?:\.\d{1,10})?$")


class ImportError(ValueError):
    """CSV does not meet the documented annual-fact schema."""


def import_csv(content: bytes, *, financial_group: bool = False) -> Dataset:
    if not content or len(content) > MAX_CSV_BYTES:
        raise ImportError("CSV must contain data and be at most 1 MiB.")
    try:
        text = content.decode("utf-8-sig")
        if "\x00" in text:
            raise ImportError("CSV contains binary/null characters.")
        reader = csv.DictReader(io.StringIO(text), strict=True)
        if reader.fieldnames != list(COLUMNS):
            raise ImportError(
                "Unsupported CSV columns/order. Use the documented schema_version 1 template."
            )
        rows = list(reader)
    except (UnicodeError, csv.Error) as exc:
        raise ImportError("Use a well-formed UTF-8 CSV file.") from exc
    if not rows or len(rows) > MAX_ROWS:
        raise ImportError("Supply 1–1,000 fact rows.")
    facts, periods, warnings, seen = [], {}, [], set()
    identity = None
    currency = None
    digest = hashlib.sha256(content).hexdigest()
    for number, row in enumerate(rows, 2):
        try:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Row has the wrong number of columns.")
            if any(len(value) > 500 for value in row.values()):
                raise ValueError("A field exceeds 500 characters.")
            if row["schema_version"] != "1":
                raise ValueError("Unsupported schema_version; expected 1.")
            if not row["company"].strip() or not row["source_reference"].strip():
                raise ValueError("Company and source_reference must be supplied.")
            if not re.fullmatch(r"\d{4}", row["fiscal_year"]):
                raise ValueError("fiscal_year must be four digits.")
            for key in ("period_start", "period_end"):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[key]):
                    raise ValueError(f"{key}: use YYYY-MM-DD.")
            period = Period(
                fiscal_year=int(row["fiscal_year"]),
                start=row["period_start"],
                end=row["period_end"],
            )
            metric = Metric(row["metric"])
            key = (period.end, metric)
            if key in seen:
                raise ValueError(
                    "Duplicate/conflicting metric and period; resolve before importing."
                )
            seen.add(key)
            if period.end in periods and periods[period.end] != period:
                raise ValueError("Inconsistent fiscal year or period start for the same endpoint.")
            periods[period.end] = period
            this_identity = (row["company"], row["cik"])
            if identity is not None and this_identity != identity:
                raise ValueError("One company and CIK per upload.")
            identity = this_identity
            if row["unit"] != row["currency"] or not re.fullmatch(r"[A-Z]{3}", row["currency"]):
                raise ValueError(
                    "Use three-letter currency codes and whole currency units (e.g. USD/USD)."
                )
            if currency and currency != row["currency"]:
                raise ValueError("Mixed currencies are unsupported; no automatic FX conversion.")
            currency = row["currency"]
            if row["value"] == "":
                warnings.append(
                    Warning(
                        code="MISSING_VALUE",
                        message=f"Row {number}: value explicitly missing.",
                        period_end=period.end,
                        metric=metric,
                    )
                )
                continue
            if not NUMBER.fullmatch(row["value"]):
                raise ValueError(
                    "Value must be a plain finite decimal, without commas, exponent or formula."
                )
            value = Decimal(row["value"])
            if metric in {Metric.CAPEX, Metric.INVESTMENT_PURCHASES} and value < 0:
                raise ValueError(
                    "capex must be a positive outflow; confirm and correct the source sign."
                )
            facts.append(
                Fact(
                    company=row["company"],
                    cik=row["cik"],
                    metric=metric,
                    concept=f"manual:{metric.value}",
                    value=value,
                    original_value=row["value"],
                    currency=currency,
                    unit=row["unit"],
                    start=None if metric in INSTANT_METRICS else period.start,
                    end=period.end,
                    fiscal_year=period.fiscal_year,
                    kind="instant" if metric in INSTANT_METRICS else "duration",
                    form="CSV",
                    source_id=f"upload:{digest}:row:{number}: {row['source_reference']}",
                    status="user_provided",
                )
            )
        except (ValidationError, ValueError) as exc:
            # Do not include raw uploaded data in diagnostic logs or UI exceptions.
            message = exc.errors()[0]["msg"] if isinstance(exc, ValidationError) else str(exc)
            raise ImportError(f"Row {number}: {message}") from exc
    if not facts:
        raise ImportError("At least one numeric observation is required.")
    ordered = sorted(periods.values(), key=lambda p: p.end)
    if any(current.start <= prior.end for prior, current in zip(ordered, ordered[1:])):
        raise ImportError("Annual reporting intervals overlap; review the supplied periods.")
    for period in periods.values():
        for metric in BASE_METRICS:
            if not any(f.end == period.end and f.metric == metric for f in facts):
                warnings.append(
                    Warning(
                        code="MISSING_METRIC",
                        message=f"No {metric.value} supplied.",
                        period_end=period.end,
                        metric=metric,
                    )
                )
    try:
        return Dataset(
            company=identity[0],
            cik=identity[1],
            origin="csv",
            fetched_at=datetime.now(timezone.utc),
            periods=tuple(sorted(periods.values(), key=lambda p: p.end)),
            observations=tuple(facts),
            selected_ids=tuple(f.id for f in facts),
            warnings=tuple(warnings),
            policy="User-provided annual data; no SEC verification or independent source confirmation.",
            source_hashes={"uploaded_csv": digest},
            accounting_basis="user-provided",
            financial_group=financial_group or identity[1] == "0001985487",
            metrics=BASE_METRICS
            + tuple(
                m for m in Metric if m not in BASE_METRICS and any(f.metric == m for f in facts)
            ),
        )
    except ValidationError as exc:
        raise ImportError(exc.errors()[0]["msg"]) from exc
