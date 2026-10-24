"""Narrow, reviewed company reporting profiles; never guess accounting equivalence."""

from dataclasses import dataclass

from finsight.models import Metric

US_CONCEPTS = {
    Metric.REVENUE: ("RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"),
    Metric.OPERATING_PROFIT: ("OperatingIncomeLoss",),
    Metric.NET_INCOME: ("NetIncomeLoss",),
    Metric.OPERATING_CASH_FLOW: ("NetCashProvidedByUsedInOperatingActivities",),
    Metric.CAPEX: ("PaymentsToAcquirePropertyPlantAndEquipment",),
    Metric.CASH: ("CashAndCashEquivalentsAtCarryingValue",),
    Metric.ASSETS: ("Assets",),
    Metric.LIABILITIES: ("Liabilities",),
}
KSPI_CONCEPTS = {
    Metric.REVENUE: ("Revenue",),
    Metric.OPERATING_PROFIT: (),  # Pretax profit is not substituted for operating profit.
    Metric.NET_INCOME: ("ProfitLoss",),
    Metric.OPERATING_CASH_FLOW: ("CashFlowsFromUsedInOperatingActivities",),
    Metric.CAPEX: (),  # Broader PPE+intangibles line is kept as a distinct metric below.
    Metric.CASH: ("CashAndCashEquivalents",),
    Metric.ASSETS: ("Assets",),
    Metric.LIABILITIES: ("Liabilities",),
    Metric.PARENT_NET_INCOME: ("ProfitLossAttributableToOwnersOfParent",),
    Metric.PRETAX_PROFIT: ("ProfitLossBeforeTax",),
    Metric.INVESTMENT_PURCHASES: (
        "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets",
    ),
}


@dataclass(frozen=True)
class ReportingProfile:
    accounting_basis: str
    taxonomy: str
    currency: str
    annual_form: str
    financial_group: bool
    concepts: dict[Metric, tuple[str, ...]]


US_GAAP = ReportingProfile("US GAAP", "us-gaap", "USD", "10-K", False, US_CONCEPTS)
KSPI_IFRS = ReportingProfile("IFRS", "ifrs-full", "KZT", "20-F", True, KSPI_CONCEPTS)


def profile_for(cik: str) -> ReportingProfile:
    return KSPI_IFRS if cik == "0001985487" else US_GAAP
