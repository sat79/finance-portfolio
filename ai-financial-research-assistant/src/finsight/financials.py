"""Pure arithmetic and conservative comparability gates; no network or UI."""

from decimal import Decimal, localcontext

from finsight.models import Calculation, Dataset, Fact, Metric, Period


def _finite(*values: Decimal) -> None:
    if any(not isinstance(value, Decimal) or not value.is_finite() for value in values):
        raise ValueError("Inputs must be finite Decimal values.")


def growth_percent(current: Decimal, previous: Decimal) -> Decimal:
    _finite(current, previous)
    if previous <= 0 or current < 0:
        raise ValueError("Growth requires a positive base and non-negative current revenue.")
    return (current / previous - 1) * 100


def margin_percent(profit: Decimal, revenue: Decimal) -> Decimal:
    _finite(profit, revenue)
    if revenue <= 0:
        raise ValueError("Margin requires positive revenue.")
    return profit / revenue * 100


def fcf_proxy(cfo: Decimal, capex: Decimal) -> Decimal:
    _finite(cfo, capex)
    if capex < 0:
        raise ValueError("PP&E purchases must be a positive outflow; sign needs review.")
    with localcontext() as context:
        context.prec = 40  # Exact subtraction for the schema's <=30-digit source amounts.
        return cfo - capex


def comparable_periods(current: Period, prior: Period) -> bool:
    return (
        current.fiscal_year == prior.fiscal_year + 1
        and 350 <= (current.end - prior.end).days <= 380
        and abs((current.start - prior.end).days - 1) <= 7
        and abs((current.end - current.start).days - (prior.end - prior.start).days) <= 7
    )


def calculate(dataset: Dataset) -> list[Calculation]:
    lookup = {(f.end, f.metric): f for f in dataset.selected}
    results = []
    periods = sorted(dataset.periods, key=lambda p: p.end)

    def derive(period, name, unit, formula, inputs, function, issue=None):
        facts: list[Fact] = [f for f in inputs if f is not None]
        warning = issue
        value = None
        if warning:
            pass
        elif len(facts) != len(inputs):
            warning = "Missing required input; no value calculated."
        elif len({(f.currency, f.unit) for f in facts}) != 1:
            warning = "Incompatible currencies or units."
        elif (
            len({f.end for f in facts}) == 1
            and all(f.status == "reported" for f in facts)
            and len({f.accession for f in facts}) > 1
        ):
            warning = (
                "Inputs come from different SEC filings; reconcile their accounting basis first."
            )
        if not warning:
            try:
                value = function(*(f.value for f in facts))
            except ValueError as exc:
                warning = str(exc)
        results.append(
            Calculation(
                period_end=period.end,
                metric=name,
                value=value,
                unit=unit,
                formula=formula,
                input_ids=tuple(f.id for f in facts),
                warning=warning,
            )
        )

    for index, period in enumerate(periods):

        def get(metric):
            return lookup.get((period.end, metric))

        revenue = get(Metric.REVENUE)
        prior = periods[index - 1] if index else None
        prior_revenue = lookup.get((prior.end, Metric.REVENUE)) if prior else None
        issue = None
        if prior and not comparable_periods(period, prior):
            issue = "Non-consecutive or non-comparable annual periods."
        if revenue and prior_revenue and revenue.concept != prior_revenue.concept:
            issue = "Revenue concept changed; review accounting comparability."
        derive(
            period,
            "revenue_growth",
            "percent",
            "(revenue / prior_revenue - 1) * 100",
            [revenue, prior_revenue],
            growth_percent,
            issue,
        )
        derive(
            period,
            "operating_margin",
            "percent",
            "operating_profit / revenue * 100",
            [get(Metric.OPERATING_PROFIT), revenue],
            margin_percent,
        )
        derive(
            period,
            "net_margin",
            "percent",
            "net_income / revenue * 100",
            [get(Metric.NET_INCOME), revenue],
            margin_percent,
        )
        cfo, capex = get(Metric.OPERATING_CASH_FLOW), get(Metric.CAPEX)
        derive(
            period,
            "fcf_proxy",
            cfo.currency if cfo else "currency",
            "operating_cash_flow - purchases_of_PPE (positive outflow)",
            [cfo, capex],
            fcf_proxy,
            (
                "Not presented for a financial group: lending/deposit cash flows and regulatory capital "
                "make this simple proxy unsuitable as distributable cash."
            )
            if dataset.financial_group
            else None,
        )
    return results


def commentary(dataset: Dataset, results: list[Calculation]) -> list[str]:
    """Observations only: no causal explanations or model-generated text."""
    lines = []
    lookup = {(r.period_end, r.metric): r for r in results}
    periods = sorted(dataset.periods, key=lambda p: p.end)
    for index, period in enumerate(periods):
        growth = lookup[(period.end, "revenue_growth")].value
        if growth is not None:
            direction = (
                "increased" if growth > 0 else "decreased" if growth < 0 else "was unchanged"
            )
            lines.append(
                f"{period.label}: revenue {direction}"
                + (f" by {abs(growth):.2f}%." if growth else ".")
            )
        margin = lookup[(period.end, "operating_margin")].value
        if index and comparable_periods(period, periods[index - 1]):
            prior = lookup[(periods[index - 1].end, "operating_margin")].value
            facts = {(f.end, f.metric): f for f in dataset.selected}
            inputs = [
                facts.get((p.end, m))
                for p in (periods[index - 1], period)
                for m in (Metric.REVENUE, Metric.OPERATING_PROFIT)
            ]
            safe = (
                all(inputs)
                and len({f.currency for f in inputs}) == 1
                and inputs[0].concept == inputs[2].concept
                and inputs[1].concept == inputs[3].concept
            )
            if safe and margin is not None and prior is not None:
                change = margin - prior
                direction = (
                    "improved" if change > 0 else "declined" if change < 0 else "was unchanged"
                )
                lines.append(
                    f"{period.label}: operating margin {direction}"
                    + (f" by {abs(change):.2f} percentage points." if change else ".")
                )
                if growth is not None and growth > 0 and change < 0:
                    lines.append(f"{period.label}: revenue rose while operating margin declined.")
        fcf = lookup[(period.end, "fcf_proxy")]
        if fcf.value is not None and fcf.value < 0:
            lines.append(
                f"{period.label}: the CFO less PP&E purchases cash-flow proxy was negative."
            )
    return lines
