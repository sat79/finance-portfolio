from copy import deepcopy
from datetime import datetime, timezone

import pytest

from finsight.models import Metric
from finsight.sec import SECError
from finsight.selection import CONCEPTS, select_annual


def select(raw, submissions):
    return select_annual(
        raw,
        submissions,
        cik="0000000001",
        origin="synthetic_fixture",
        fetched_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def revenue(raw):
    return raw["facts"]["us-gaap"][CONCEPTS[Metric.REVENUE][0]]["units"]["USD"]


def test_non_calendar_year_and_instant(dataset):
    assert [(p.start.month, p.end.month) for p in dataset.periods] == [(7, 6)] * 3
    assert len(dataset.selected) == 24
    assert all(f.start is None for f in dataset.selected if f.metric == Metric.ASSETS)
    assert all(f.source_url is None and f.status == "synthetic" for f in dataset.selected)


def test_quarters_and_segments_excluded(raw, submissions):
    rows = revenue(raw)
    rows.extend(
        [
            dict(rows[2], start="2024-04-01", val=999),
            dict(rows[2], dimensions={"segment": "wrong"}, val=999),
            dict(rows[2], form="10-Q", val=999),
        ]
    )
    data = select(raw, submissions)
    assert (
        next(f.value for f in data.selected if f.metric == Metric.REVENUE and f.end.year == 2024)
        == 1500
    )
    assert any(w.code == "DIMENSION_EXCLUDED" for w in data.warnings)


def test_later_comparative_not_labelled_as_later_fiscal_year(raw, submissions):
    rows = revenue(raw)
    rows.append(dict(rows[0], fy=2024, filed="2024-08-01", accn=rows[2]["accn"], val=1050))
    data = select(raw, submissions)
    f = next(f for f in data.selected if f.metric == Metric.REVENUE and f.end.year == 2022)
    assert f.fiscal_year == 2022 and f.source_fiscal_year == 2024 and f.value == 1050
    assert len(data.observations) == 25
    assert any(w.code == "COMPETING_VALUES" for w in data.warnings)


def test_amendments_explicit(raw, submissions):
    rows = revenue(raw)
    rows.append(
        dict(rows[2], filed="2024-09-01", accn="0000000001-24-000002", form="10-K/A", val=1450)
    )
    data = select(raw, submissions)
    assert (
        next(f.value for f in data.selected if f.metric == Metric.REVENUE and f.end.year == 2024)
        == 1450
    )
    assert any(w.code == "AMENDMENT_SELECTED" for w in data.warnings)


def test_same_day_conflicts_stay_missing(raw, submissions):
    rows = revenue(raw)
    rows.append(dict(rows[2], val=999))
    data = select(raw, submissions)
    assert not any(f for f in data.selected if f.metric == Metric.REVENUE and f.end.year == 2024)
    assert any(w.code == "AMBIGUOUS_LATEST" for w in data.warnings)


def test_conflicting_concepts_not_arbitrarily_chosen(raw, submissions):
    raw["facts"]["us-gaap"]["SalesRevenueNet"] = {
        "units": {"USD": [dict(revenue(raw)[2], val=999)]}
    }
    data = select(raw, submissions)
    assert not any(f for f in data.selected if f.metric == Metric.REVENUE and f.end.year == 2024)


def test_duplicate_identical_fact_is_deduplicated(raw, submissions):
    revenue(raw).append(deepcopy(revenue(raw)[0]))
    assert len(select(raw, submissions).observations) == 24


def test_malformed_value_and_non_usd_warn(raw, submissions):
    revenue(raw)[0]["val"] = "NaN"
    raw["facts"]["us-gaap"]["Assets"]["units"] = {
        "EUR": raw["facts"]["us-gaap"]["Assets"]["units"]["USD"]
    }
    data = select(raw, submissions)
    assert any(w.code == "INVALID_OBSERVATION" for w in data.warnings)
    assert any(w.code == "UNSUPPORTED_UNIT" for w in data.warnings)
    assert not any(f.metric == Metric.ASSETS for f in data.selected)


def test_cik_mismatch_rejected(raw, submissions):
    raw["cik"] = 2
    with pytest.raises(SECError, match="identities"):
        select(raw, submissions)


def test_short_year_and_malformed_schema_rejected(raw, submissions):
    for entry in raw["facts"]["us-gaap"].values():
        for row in entry["units"]["USD"]:
            if "start" in row:
                row["start"] = row["end"][:4] + "-01-01"
    with pytest.raises(SECError, match="annual periods"):
        select(raw, submissions)
    with pytest.raises(SECError, match="schema"):
        select({}, {})


def test_53_week_year_is_flagged(raw, submissions):
    for concept in raw["facts"]["us-gaap"].values():
        for row in concept["units"]["USD"]:
            if row["end"] == "2024-06-30":
                row["end"] = "2024-07-06"
    submissions["filings"]["recent"]["reportDate"][-1] = "2024-07-06"
    data = select(raw, submissions)
    assert any(w.code == "LONG_FISCAL_YEAR" for w in data.warnings)
    assert data.periods[-1].fiscal_year == 2024
