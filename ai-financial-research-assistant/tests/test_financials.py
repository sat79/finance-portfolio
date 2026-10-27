from decimal import Decimal as D

import pytest

from finsight.financials import calculate, commentary, fcf_proxy, growth_percent, margin_percent
from finsight.models import Dataset, Metric


def result(dataset, year, metric):
    return next(c for c in calculate(dataset) if c.period_end.year == year and c.metric == metric)


def test_independent_hand_calculations(dataset):
    assert result(dataset, 2023, "revenue_growth").value == D(20)
    assert result(dataset, 2024, "revenue_growth").value == D(25)
    assert result(dataset, 2023, "operating_margin").value == D(8)
    assert result(dataset, 2023, "net_margin").value == D(-2)
    assert result(dataset, 2023, "fcf_proxy").value == D(-50)
    assert result(dataset, 2024, "fcf_proxy").value == D(150)
    assert result(dataset, 2022, "revenue_growth").value is None
    for calc in calculate(dataset):
        assert set(calc.input_ids) <= set(dataset.selected_ids)


@pytest.mark.parametrize(
    "function,args",
    [
        (growth_percent, [D(10), D(0)]),
        (growth_percent, [D(10), D(-1)]),
        (growth_percent, [D(-10), D(1)]),
        (margin_percent, [D(-10), D(0)]),
        (fcf_proxy, [D(100), D(-2)]),
    ],
)
def test_invalid_denominators_and_signs(function, args):
    with pytest.raises(ValueError):
        function(*args)


def test_losses_are_valid():
    assert margin_percent(D(-20), D(100)) == -20
    assert fcf_proxy(D(-10), D(20)) == -30
    assert growth_percent(D(0), D(100)) == -100


def changed(dataset, edit):
    facts = tuple(edit(f) for f in dataset.observations)
    return Dataset(
        **{
            **dataset.model_dump(),
            "observations": facts,
            "selected_ids": tuple(f.id for f in facts),
        }
    )


def test_currency_mismatch_is_not_calculated(dataset):
    data = changed(
        dataset,
        lambda f: (
            f.model_copy(update={"currency": "EUR", "unit": "EUR"})
            if f.metric == Metric.CAPEX
            else f
        ),
    )
    assert result(data, 2024, "fcf_proxy").value is None
    assert "currencies" in result(data, 2024, "fcf_proxy").warning


def test_missing_not_zero(dataset):
    facts = tuple(f for f in dataset.observations if f.metric != Metric.OPERATING_PROFIT)
    data = Dataset(
        **{
            **dataset.model_dump(),
            "observations": facts,
            "selected_ids": tuple(f.id for f in facts),
        }
    )
    assert result(data, 2024, "operating_margin").value is None
    assert result(data, 2024, "net_margin").value == 8


def test_concept_change_blocks_growth(dataset):
    data = changed(
        dataset,
        lambda f: (
            f.model_copy(update={"concept": "different:revenue"})
            if f.metric == Metric.REVENUE and f.end.year == 2024
            else f
        ),
    )
    assert "concept changed" in result(data, 2024, "revenue_growth").warning


def test_commentary_percentage_points_and_no_inferred_cause(dataset):
    text = "\n".join(commentary(dataset, calculate(dataset)))
    assert "declined by 2.00 percentage points" in text
    assert "increased by 20.00%" in text
    assert "cash-flow proxy was negative" in text
    assert "while operating margin declined" in text
    assert "because" not in text


def test_missing_year_blocks_growth(dataset):
    facts = tuple(f for f in dataset.observations if f.end.year != 2023)
    data = Dataset(
        **{
            **dataset.model_dump(),
            "observations": facts,
            "selected_ids": tuple(f.id for f in facts),
            "periods": tuple(p for p in dataset.periods if p.fiscal_year != 2023),
        }
    )
    assert result(data, 2024, "revenue_growth").value is None
    assert "Non-consecutive" in result(data, 2024, "revenue_growth").warning


@pytest.mark.parametrize("value", [D("NaN"), D("Infinity"), D("-Infinity")])
def test_nonfinite_inputs_rejected(value):
    for function in [growth_percent, margin_percent, fcf_proxy]:
        with pytest.raises(ValueError, match="finite"):
            function(value, D(100))


def test_mixed_filing_basis_suppresses_same_period_ratios(dataset):
    from finsight.models import Fact, filing_url

    facts = []
    for fact in dataset.observations:
        accession = fact.accession
        if fact.metric == Metric.REVENUE:
            accession = accession.replace("000001", "000002")
        facts.append(
            Fact(
                **{
                    **fact.model_dump(),
                    "accession": accession,
                    "status": "reported",
                    "source_url": filing_url(fact.cik, accession),
                }
            )
        )
    data = Dataset(
        **{
            **dataset.model_dump(),
            "observations": tuple(facts),
            "selected_ids": tuple(f.id for f in facts),
        }
    )
    assert result(data, 2024, "operating_margin").value is None
    assert "different SEC filings" in result(data, 2024, "operating_margin").warning
    assert result(data, 2024, "fcf_proxy").value == 150


def test_frozen_real_company_reconciliation():
    import json
    from pathlib import Path

    evidence = json.loads(
        (Path(__file__).parent / "fixtures/reconciled_companies.json").read_text()
    )
    for company in evidence:
        data = Dataset.model_validate(company["dataset"])
        for fact in data.selected:
            assert fact.value == D(company["expected"][str(fact.fiscal_year)][fact.metric.value])
            assert fact.source_url and fact.accession
        if company["ticker"] == "AAPL":
            assert result(data, 2025, "fcf_proxy").value == D("98767000000")
            assert round(result(data, 2025, "operating_margin").value, 4) == D("31.9708")
            assert round(result(data, 2024, "revenue_growth").value, 4) == D("2.0220")
        elif company["ticker"] == "MSFT":
            assert result(data, 2026, "fcf_proxy").value == D("66987000000")
            assert round(result(data, 2026, "operating_margin").value, 4) == D("46.7808")
            assert round(result(data, 2025, "revenue_growth").value, 4) == D("14.9322")
        else:
            assert company["ticker"] == "KSPI"
            assert result(data, 2025, "fcf_proxy").value is None
            assert round(result(data, 2025, "net_margin").value, 4) == D("26.3887")
            assert data.accounting_basis == "IFRS" and data.financial_group


def test_cash_proxy_preserves_schema_precision():
    assert fcf_proxy(D("99999999999999999999.1234567890"), D("0.0000000001")) == D(
        "99999999999999999999.1234567889"
    )
