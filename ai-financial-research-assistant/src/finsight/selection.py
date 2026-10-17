"""Conservative annual 10-K selection. Competing accepted observations remain inspectable."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from pydantic import ValidationError

from finsight.models import INSTANT_METRICS, Dataset, Fact, Metric, Period, Warning, filing_url
from finsight.sec import SECError

CONCEPTS = {
    Metric.REVENUE: ("RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"),
    Metric.OPERATING_PROFIT: ("OperatingIncomeLoss",),
    Metric.NET_INCOME: ("NetIncomeLoss",),
    Metric.OPERATING_CASH_FLOW: ("NetCashProvidedByUsedInOperatingActivities",),
    Metric.CAPEX: ("PaymentsToAcquirePropertyPlantAndEquipment",),
    Metric.CASH: ("CashAndCashEquivalentsAtCarryingValue",),
    Metric.ASSETS: ("Assets",),
    Metric.LIABILITIES: ("Liabilities",),
}
POLICY = (
    "Latest available annual 10-K/10-K/A observation for each exact fiscal interval and metric. "
    "Annual endpoints and fiscal-year labels anchored to the company's own 10-K disclosures. "
    "Same-date conflicts stay missing. Different concept values stay missing. "
    "Competing observations retained. This is not a historical point-in-time series."
)


def select_annual(
    companyfacts: dict,
    submissions: dict,
    *,
    cik: str,
    origin: str,
    fetched_at: datetime,
    source_hashes=None,
) -> Dataset:
    warnings = []

    def warn(code, message, end=None, metric=None):
        warnings.append(Warning(code=code, message=message, period_end=end, metric=metric))

    try:
        if (
            str(int(companyfacts["cik"])).zfill(10) != cik
            or str(int(submissions["cik"])).zfill(10) != cik
        ):
            raise SECError("CompanyFacts and submissions identities disagree.")
        company = companyfacts["entityName"]
        recent = submissions["filings"]["recent"]
        columns = [recent[k] for k in ("accessionNumber", "form", "reportDate", "filingDate")]
        if len({len(c) for c in columns}) != 1:
            raise SECError("SEC filing columns have inconsistent lengths.")
        filings = [
            dict(zip(("accn", "form", "end", "filed"), row))
            for row in zip(*columns)
            if row[1] in {"10-K", "10-K/A"}
        ]
        taxonomy = companyfacts["facts"]["us-gaap"]
        if not isinstance(taxonomy, dict) or not isinstance(company, str):
            raise SECError("Unexpected SEC financial schema.")
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, SECError):
            raise
        raise SECError(
            "SEC response lacks the required company or US GAAP annual filing schema."
        ) from exc

    raw = []
    for metric, concepts in CONCEPTS.items():
        for concept in concepts:
            try:
                units = taxonomy.get(concept, {}).get("units", {})
                for unit, rows in units.items():
                    for row in rows:
                        if not isinstance(row, dict):
                            raise SECError("Malformed SEC fact observation.")
                        if row.get("form") not in {"10-K", "10-K/A"} or row.get("fp") != "FY":
                            continue
                        if any(row.get(k) for k in ("segment", "dimensions")):
                            warn(
                                "DIMENSION_EXCLUDED", f"Excluded dimensional {concept} observation."
                            )
                            continue
                        raw.append((metric, concept, unit, row))
            except (AttributeError, TypeError) as exc:
                raise SECError("Malformed SEC concept/units structure.") from exc

    # A comparative observation's 'fy' is the filing's FY, not the fact's period year.
    # Use only duration facts in an endpoint's own 10-K accession to establish its FY/start.
    periods = []
    for endpoint in sorted({f["end"] for f in filings}, reverse=True)[:5]:
        try:
            end = date.fromisoformat(endpoint)
        except (ValueError, TypeError):
            warn("INVALID_REPORT_DATE", "A filing has an invalid report date; excluded.")
            continue
        own = {f["accn"] for f in filings if f["end"] == endpoint and f["form"] == "10-K"}
        anchors = set()
        for metric, _, unit, row in raw:
            if (
                row.get("accn") not in own
                or row.get("end") != endpoint
                or metric in INSTANT_METRICS
                or unit != "USD"
            ):
                continue
            try:
                start = date.fromisoformat(row["start"])
                if 350 <= (end - start).days + 1 <= 380:
                    anchors.add((start, int(row["fy"])))
            except (KeyError, ValueError, TypeError):
                continue
        if len(anchors) != 1:
            warn(
                "ANNUAL_ANCHOR_UNCLEAR",
                "Cannot establish one annual start and fiscal-year label; "
                "period excluded (short transition years are unsupported).",
                end,
            )
            continue
        start, year = anchors.pop()
        periods.append(Period(start=start, end=end, fiscal_year=year))
    if not periods:
        raise SECError("No unambiguous supported annual periods found in recent 10-K filings.")
    observations = {}
    selected = []
    for period in sorted(periods, key=lambda p: p.end):
        by_metric = defaultdict(list)
        for metric, concept, unit, row in raw:
            if row.get("end") != period.end.isoformat():
                continue
            if metric not in INSTANT_METRICS and row.get("start") != period.start.isoformat():
                continue
            if metric in INSTANT_METRICS and row.get("start"):
                continue
            if unit != "USD":
                warn(
                    "UNSUPPORTED_UNIT",
                    f"Excluded {concept} unit {unit}; SEC MVP requires USD.",
                    period.end,
                    metric,
                )
                continue
            try:
                accession = row["accn"]
                fact = Fact(
                    company=company,
                    cik=cik,
                    metric=metric,
                    concept=f"us-gaap:{concept}",
                    value=Decimal(str(row["val"])),
                    original_value=str(row["val"]),
                    currency=unit,
                    unit=unit,
                    start=None if metric in INSTANT_METRICS else period.start,
                    end=period.end,
                    fiscal_year=period.fiscal_year,
                    source_fiscal_year=row.get("fy"),
                    kind="instant" if metric in INSTANT_METRICS else "duration",
                    form=row["form"],
                    filed=row["filed"],
                    accession=accession,
                    source_url=None
                    if origin == "synthetic_fixture"
                    else filing_url(cik, accession),
                    source_id=(
                        f"synthetic:{concept}:{accession}"
                        if origin == "synthetic_fixture"
                        else f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json#us-gaap/{concept}"
                    ),
                    status="synthetic" if origin == "synthetic_fixture" else "reported",
                )
            except (ValidationError, ValueError, KeyError, TypeError, ArithmeticError):
                warn(
                    "INVALID_OBSERVATION",
                    f"Malformed {concept} annual observation excluded.",
                    period.end,
                    metric,
                )
                continue
            observations[fact.id] = fact
            by_metric[metric].append(fact)
        for metric in Metric:
            candidates = list({f.id: f for f in by_metric[metric]}.values())
            if not candidates:
                warn(
                    "MISSING_METRIC",
                    f"No supported {metric.value} observation for this period.",
                    period.end,
                    metric,
                )
                continue
            if len({f.value for f in candidates}) > 1:
                warn(
                    "COMPETING_VALUES",
                    "Different disclosed values retained; latest filing policy applied. "
                    "This may reflect revision, reclassification or error; inspect the filings.",
                    period.end,
                    metric,
                )
            # Do not assume similarly named tags are interchangeable. Compare latest per concept.
            latest = []
            for concept in {f.concept for f in candidates}:
                group = [f for f in candidates if f.concept == concept]
                last_date = max(f.filed for f in group)
                latest.extend(f for f in group if f.filed == last_date)
            if len({f.value for f in latest}) != 1:
                warn(
                    "AMBIGUOUS_LATEST",
                    "Conflicting latest disclosures or concepts; no value selected.",
                    period.end,
                    metric,
                )
                continue
            # Equal values: deterministic latest filing, then published concept preference and accession.
            latest.sort(
                key=lambda f: (
                    -f.filed.toordinal(),
                    CONCEPTS[metric].index(f.concept.split(":")[1]),
                    f.accession,
                )
            )
            winner = latest[0]
            selected.append(winner.id)
            if winner.form == "10-K/A":
                warn(
                    "AMENDMENT_SELECTED",
                    "Selected a later 10-K/A observation; review amendment scope.",
                    period.end,
                    metric,
                )
            if winner.source_fiscal_year != period.fiscal_year:
                warn(
                    "LATER_COMPARATIVE",
                    "Value comes from a later filing's comparative disclosure.",
                    period.end,
                    metric,
                )
        if (period.end - period.start).days + 1 > 367:
            warn(
                "LONG_FISCAL_YEAR",
                "53-week year: growth is not adjusted for the extra week.",
                period.end,
            )
    warn("POLICY", POLICY)
    warn(
        "SCOPE",
        "AAPL/MSFT, USD, US GAAP, consolidated companyfacts and recent 10-K history only. "
        "Custom tags, segments, short transition years and accounting-basis changes need manual review.",
    )
    return Dataset(
        company=company,
        cik=cik,
        origin=origin,
        fetched_at=fetched_at,
        periods=tuple(sorted(periods, key=lambda p: p.end)),
        observations=tuple(observations.values()),
        selected_ids=tuple(selected),
        warnings=tuple(warnings),
        policy=POLICY,
        source_hashes=source_hashes or {},
    )
