"""KSPI-specific regression checks: real frozen disclosures, IFRS/KZT and financial-group controls."""

import json
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from finsight.csv_import import import_csv
from finsight.financials import calculate
from finsight.models import Metric
from finsight.sec import SUPPORTED
from finsight.selection import select_annual

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def kspi_raw():
    return json.loads((FIXTURES / "kspi_companyfacts.json").read_text())


@pytest.fixture
def kspi_submissions():
    return json.loads((FIXTURES / "kspi_submissions.json").read_text())


def load(raw, submissions):
    return select_annual(
        raw,
        submissions,
        cik="0001985487",
        origin="sec_cache",
        fetched_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
    )


def test_all_three_supported_kspi_default():
    assert set(SUPPORTED) == {"KSPI", "AAPL", "MSFT"}
    assert next(iter(SUPPORTED)) == "KSPI"


def test_ifrs_20f_kzt_three_years(kspi_raw, kspi_submissions):
    data = load(kspi_raw, kspi_submissions)
    assert data.accounting_basis == "IFRS" and data.financial_group
    assert [p.fiscal_year for p in data.periods] == [2023, 2024, 2025]
    assert len(data.selected) == 27
    assert {f.currency for f in data.selected} == {"KZT"}
    assert {f.form for f in data.selected} == {"20-F"}
    assert all(f.concept.startswith("ifrs-full:") and f.source_url for f in data.selected)


def test_after_rewards_revenue_and_profit_attribution(kspi_raw, kspi_submissions):
    data = load(kspi_raw, kspi_submissions)
    values = {f.metric: f.value for f in data.selected if f.fiscal_year == 2025}
    assert values[Metric.REVENUE] == Decimal("4046074000000")
    assert values[Metric.REVENUE] != Decimal("4101961000000")  # Segment revenue before rewards.
    assert values[Metric.NET_INCOME] == Decimal("1067707000000")
    assert values[Metric.PARENT_NET_INCOME] == Decimal("1073177000000")
    assert any(w.code == "KSPI_REVENUE_BASIS" for w in data.warnings)


def test_broad_purchases_and_pretax_profit_not_substituted(kspi_raw, kspi_submissions):
    data = load(kspi_raw, kspi_submissions)
    metrics = {f.metric for f in data.selected}
    assert Metric.PRETAX_PROFIT in metrics and Metric.INVESTMENT_PURCHASES in metrics
    assert Metric.OPERATING_PROFIT not in metrics and Metric.CAPEX not in metrics
    results = calculate(data)
    assert all(c.value is None for c in results if c.metric in ["operating_margin", "fcf_proxy"])
    assert all("financial group" in c.warning for c in results if c.metric == "fcf_proxy")
    margin = next(
        c.value for c in results if c.period_end.year == 2025 and c.metric == "net_margin"
    )
    assert round(margin, 4) == Decimal("26.3887")


def test_us_gaap_tags_do_not_leak_into_ifrs_selection(kspi_raw, kspi_submissions):
    kspi_raw["facts"]["us-gaap"] = {
        "OperatingIncomeLoss": {
            "units": {
                "KZT": [
                    {
                        "start": "2025-01-01",
                        "end": "2025-12-31",
                        "val": 999,
                        "form": "20-F",
                        "fp": "FY",
                        "fy": 2025,
                        "filed": "2026-03-16",
                        "accn": "0001985487-26-000008",
                    }
                ]
            }
        }
    }
    data = load(kspi_raw, kspi_submissions)
    assert not any(f.metric == Metric.OPERATING_PROFIT for f in data.selected)


def test_wrong_currency_excluded_not_converted(kspi_raw, kspi_submissions):
    units = kspi_raw["facts"]["ifrs-full"]["Revenue"]["units"]
    units["USD"] = deepcopy(units.pop("KZT"))
    data = load(kspi_raw, kspi_submissions)
    assert not any(f.metric == Metric.REVENUE for f in data.selected)
    assert any(w.code == "UNSUPPORTED_UNIT" and "KZT" in w.message for w in data.warnings)


def test_csv_financial_group_suppresses_proxy_even_with_capex():
    raw = (FIXTURES.parents[1] / "data/examples/valid_synthetic.csv").read_bytes()
    data = import_csv(raw, financial_group=True)
    assert all(c.value is None for c in calculate(data) if c.metric == "fcf_proxy")
    # Known KSPI CIK also turns this control on without a checkbox assertion.
    data = import_csv(raw.replace(b"0000000001", b"0001985487"))
    assert data.financial_group
