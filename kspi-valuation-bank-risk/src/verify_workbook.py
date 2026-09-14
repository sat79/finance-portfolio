"""Compare XLSX saved inputs/values to Python. This is not an Excel engine test."""
import argparse
import math
from pathlib import Path

from analyse import ROOT, CASE_NAMES, load_json, value_case, earnings_sensitivity
from xlsx_values import read_xlsx


def verify(path: Path) -> int:
    workbook = read_xlsx(path)
    config = load_json(ROOT / "data/assumptions.json")
    comparisons = 0

    def close(sheet: str, address: str, expected: float, formula: bool = False) -> None:
        nonlocal comparisons
        cell = workbook[sheet][address]
        actual = cell["value"]
        if not isinstance(actual, (int, float)) or not math.isclose(
            actual, expected, rel_tol=1e-10, abs_tol=1e-9
        ):
            raise ValueError(f"Mismatch at {sheet}!{address}: {actual} vs {expected}")
        if formula and not cell["formula"]:
            raise ValueError(f"Expected a formula at {sheet}!{address}")
        comparisons += 1

    mapping = {
        ("Assumptions", "D8"): "risk_free_usd", ("Assumptions", "D9"): "beta",
        ("Assumptions", "D10"): "erp", ("Assumptions", "D11"): "additional_risk_premium",
        ("Assumptions", "D16"): "pe_assumption", ("Assumptions", "D17"): "tax_assumption",
        ("Assumptions", "D18"): "funding_shock", ("Assumptions", "D19"): "credit_shock",
        ("Assumptions", "D34"): "terminal_kzt_dividend_growth",
        ("Assumptions", "D35"): "terminal_fx_depreciation",
        ("Sources", "D5"): "diluted_eps_2025_kzt", ("Sources", "D12"): "fx_reference_kzt_per_usd",
        ("Sources", "D13"): "quarterly_dividend_assumption_kzt",
        ("Sources", "D14"): "average_net_loans_kzt_bn", ("Sources", "D15"): "average_savings_kzt_bn",
        ("Sources", "D16"): "h1_group_net_income_kzt_bn",
    }
    for (sheet, address), key in mapping.items():
        close(sheet, address, config[key])
    for index, case in enumerate(CASE_NAMES):
        for year, column in enumerate("DEFGH"):
            close("Assumptions", f"{column}{24+index}", config["cases"][case]["dividend_growth"][year])
            close("Assumptions", f"{column}{29+index}", config["cases"][case]["fx_depreciation"][year])
    case = workbook["Assumptions"]["D4"]["value"]
    result = value_case(config, case)
    for address, key in {"D18": "terminal_usd_growth", "D19": "explicit_pv_usd",
                         "D21": "terminal_pv_usd", "D22": "value_usd", "D23": "terminal_share"}.items():
        close("Valuation", address, result[key], True)
    close("Summary", "D6", result["value_usd"], True)
    close("Valuation", "F43", result["value_usd"], True)
    for column, flow in zip("DEFGH", result["cashflows"]):
        for row, key in {8: "dividend_kzt", 10: "fx_kzt_per_usd", 11: "dividend_usd",
                         14: "present_value_usd"}.items():
            close("Valuation", f"{column}{row}", flow[key], True)
    risk = earnings_sensitivity(config)
    for address, key in {"D13": "funding_expense_kzt_bn", "D14": "credit_loss_expense_kzt_bn",
                         "D15": "pretax_stress_kzt_bn", "D16": "after_tax_stress_kzt_bn",
                         "D18": "stress_fraction_annualised_h1_income"}.items():
        close("Risk", address, risk[key], True)
    close("Risk", "D27", 0, True)
    close("Risk", "D28", 0, True)
    pe = config["diluted_eps_2025_kzt"] / config["fx_reference_kzt_per_usd"] * config["pe_assumption"]
    close("Valuation", "D29", pe, True)
    print(f"PASS: {comparisons} saved input/value comparisons; no cached formula errors.")
    print("This reads saved values. Recalculate in Excel after editing; it does not execute Excel.")
    return comparisons


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "models/KSPI-Valuation-and-Bank-Risk.xlsx")
    verify(parser.parse_args().workbook)
