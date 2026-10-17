"""Validated source observations and separate derived results. Amounts use Decimal."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Metric(str, Enum):
    REVENUE = "revenue"
    OPERATING_PROFIT = "operating_profit"
    NET_INCOME = "net_income"
    OPERATING_CASH_FLOW = "operating_cash_flow"
    CAPEX = "capex"
    CASH = "cash"
    ASSETS = "assets"
    LIABILITIES = "liabilities"


INSTANT_METRICS = {Metric.CASH, Metric.ASSETS, Metric.LIABILITIES}
LABELS = {
    Metric.REVENUE: "Revenue",
    Metric.OPERATING_PROFIT: "Operating profit / loss",
    Metric.NET_INCOME: "Net income / loss",
    Metric.OPERATING_CASH_FLOW: "Operating cash flow",
    Metric.CAPEX: "Purchases of PP&E (positive outflow)",
    Metric.CASH: "Cash and cash equivalents",
    Metric.ASSETS: "Total assets",
    Metric.LIABILITIES: "Total liabilities",
}


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Period(Record):
    fiscal_year: int = Field(ge=1900, le=2200)
    start: date
    end: date

    @model_validator(mode="after")
    def annual(self):
        if not 350 <= (self.end - self.start).days + 1 <= 380:
            raise ValueError(
                "Only annual periods of 350–380 days are supported; review stub years."
            )
        return self

    @property
    def label(self):
        return f"FY{self.fiscal_year} ({self.end.isoformat()})"


class Fact(Record):
    company: str = Field(min_length=1, max_length=200)
    cik: str = Field(pattern=r"^\d{10}$")
    metric: Metric
    concept: str = Field(min_length=1, max_length=200)
    value: Decimal = Field(allow_inf_nan=False, max_digits=30, decimal_places=10)
    original_value: str = Field(max_length=100)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    unit: str
    start: date | None = None
    end: date
    fiscal_year: int = Field(ge=1900, le=2200)
    source_fiscal_year: int | None = None
    fiscal_period: Literal["FY"] = "FY"
    kind: Literal["instant", "duration"]
    form: Literal["10-K", "10-K/A", "CSV"]
    filed: date | None = None
    accession: str | None = None
    source_url: str | None = None
    source_id: str = Field(min_length=1, max_length=500)
    status: Literal["reported", "user_provided", "synthetic"]
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        if self.unit != self.currency:
            raise ValueError("Use whole currency units, e.g. USD, not thousands or shares.")
        expected = "instant" if self.metric in INSTANT_METRICS else "duration"
        if self.kind != expected:
            raise ValueError(f"{self.metric.value} must be {expected}.")
        if self.kind == "instant" and self.start is not None:
            raise ValueError("Instant observations must not have a period start.")
        if self.kind == "duration":
            if self.start is None or not 350 <= (self.end - self.start).days + 1 <= 380:
                raise ValueError("Duration must be a supported annual period.")
        if self.filed and self.filed < self.end:
            raise ValueError("Filing date precedes the reporting period end.")
        if Decimal(self.original_value) != self.value:
            raise ValueError("Original source value must equal the retained value.")
        if self.status == "reported":
            if not self.accession or not re.fullmatch(r"\d{10}-\d{2}-\d{6}", self.accession):
                raise ValueError("SEC reported data require a valid accession.")
            if self.form not in {"10-K", "10-K/A"} or self.filed is None:
                raise ValueError("SEC reported data require filing metadata.")
            expected_url = filing_url(self.cik, self.accession)
            if self.source_url != expected_url:
                raise ValueError("Source URL must identify this SEC filing.")
        elif self.source_url is not None:
            raise ValueError("CSV and synthetic records use source identifiers, not verified URLs.")
        return self

    @property
    def id(self) -> str:
        raw = json.dumps(self.model_dump(mode="json"), sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:20]


class Warning(Record):
    code: str
    message: str
    period_end: date | None = None
    metric: Metric | None = None


class Dataset(Record):
    company: str
    cik: str
    origin: Literal["sec_live", "sec_cache", "csv", "synthetic_fixture"]
    fetched_at: datetime
    periods: tuple[Period, ...]
    observations: tuple[Fact, ...]
    selected_ids: tuple[str, ...]
    warnings: tuple[Warning, ...] = ()
    policy: str
    source_hashes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def selection_integrity(self):
        facts = {f.id: f for f in self.observations}
        if len(facts) != len(self.observations):
            raise ValueError("Duplicate observation IDs.")
        if len(set(self.selected_ids)) != len(self.selected_ids):
            raise ValueError("Duplicate selections.")
        if not set(self.selected_ids) <= facts.keys():
            raise ValueError("Selected fact missing from provenance.")
        if len({p.end for p in self.periods}) != len(self.periods):
            raise ValueError("Duplicate reporting periods.")
        if len({p.fiscal_year for p in self.periods}) != len(self.periods):
            raise ValueError("Conflicting fiscal-year labels.")
        keys = set()
        for f in self.observations:
            if f.cik != self.cik or f.company != self.company:
                raise ValueError("Mixed company identities.")
        for key in self.selected_ids:
            f = facts[key]
            period = next((p for p in self.periods if p.end == f.end), None)
            if not period or f.fiscal_year != period.fiscal_year:
                raise ValueError("Selected fact has no matching fiscal period.")
            if f.kind == "duration" and f.start != period.start:
                raise ValueError("Selected durations are not aligned.")
            slot = (f.end, f.metric)
            if slot in keys:
                raise ValueError("Multiple facts selected for one metric/period.")
            keys.add(slot)
        return self

    @property
    def selected(self) -> tuple[Fact, ...]:
        lookup = {f.id: f for f in self.observations}
        return tuple(lookup[key] for key in self.selected_ids)


class Calculation(Record):
    period_end: date
    metric: str
    value: Decimal | None
    unit: str
    formula: str
    input_ids: tuple[str, ...]
    status: Literal["calculated"] = "calculated"
    warning: str | None = None

    @field_validator("value")
    @classmethod
    def finite(cls, value):
        if value is not None and not value.is_finite():
            raise ValueError("Non-finite calculation.")
        return value


def filing_url(cik: str, accession: str) -> str:
    return (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession.replace('-', '')}/{accession}-index.html"
    )
