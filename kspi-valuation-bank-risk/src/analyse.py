"""KSPI dividend valuation and static earnings sensitivity. Python 3.10+.

Standard library only; no network calls. Fixed historical data and explicit
assumptions. research and code; see the investment memo for scope.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import json
import math
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
HORIZON = 5
CASE_NAMES = ("Base", "Downside", "Upside")
SEGMENTS = {"Payments", "Marketplace", "Fintech"}
PARAMETERS = {
    "quarterly_dividend_assumption_kzt", "fx_reference_kzt_per_usd",
    "risk_free_usd", "beta", "erp", "additional_risk_premium",
    "terminal_kzt_dividend_growth", "terminal_fx_depreciation",
    "diluted_eps_2025_kzt", "pe_assumption", "average_net_loans_kzt_bn",
    "average_savings_kzt_bn", "h1_group_net_income_kzt_bn", "funding_shock",
    "credit_shock", "tax_assumption",
}


class InputError(ValueError):
    """Inputs cannot support the requested calculation."""


def finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{label}: expected a numeric value")
    if not math.isfinite(value):
        raise InputError(f"{label}: expected a finite value")
    return float(value)


def load_json(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise InputError(f"Non-finite JSON constant: {value}")

    data = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    if not isinstance(data, dict):
        raise InputError(f"{path.name}: expected a JSON object")
    return data


def cost_of_equity(config: dict) -> float:
    return (config["risk_free_usd"] + config["beta"] * config["erp"]
            + config["additional_risk_premium"])


def terminal_usd_growth(config: dict) -> float:
    return ((1 + config["terminal_kzt_dividend_growth"])
            / (1 + config["terminal_fx_depreciation"]) - 1)


def validate_config(config: dict) -> None:
    required = PARAMETERS | {"as_of", "cases"}
    if set(config) != required:
        raise InputError(f"Assumption keys differ: missing {sorted(required-set(config))}; "
                         f"unexpected {sorted(set(config)-required)}")
    try:
        date.fromisoformat(config["as_of"])
    except (TypeError, ValueError) as exc:
        raise InputError("as_of: use an ISO date such as 2026-09-11") from exc
    values = {key: finite_number(config[key], key) for key in PARAMETERS}
    signed = {"terminal_kzt_dividend_growth", "terminal_fx_depreciation"}
    for key, value in values.items():
        if key not in signed and value < 0:
            raise InputError(f"{key}: must be non-negative")
    for key in ("fx_reference_kzt_per_usd", "h1_group_net_income_kzt_bn"):
        if values[key] <= 0:
            raise InputError(f"{key}: must be positive")
    for key in ("tax_assumption", "funding_shock", "credit_shock"):
        if not 0 <= values[key] <= 1:
            raise InputError(f"{key}: must lie between 0 and 1")
    if values["terminal_kzt_dividend_growth"] < -1:
        raise InputError("Terminal dividend growth cannot be below -100%")
    if values["terminal_fx_depreciation"] <= -1:
        raise InputError("Terminal FX depreciation must exceed -100%")
    ke = cost_of_equity(config)
    if ke <= 0 or ke <= terminal_usd_growth(config):
        raise InputError("Cost of equity must be positive and exceed terminal USD growth")
    if not isinstance(config["cases"], dict) or set(config["cases"]) != set(CASE_NAMES):
        raise InputError("cases: supply exactly Base, Downside and Upside")
    for name, case in config["cases"].items():
        if not isinstance(case, dict) or set(case) != {"dividend_growth", "fx_depreciation"}:
            raise InputError(f"{name}: supply dividend_growth and fx_depreciation")
        for key, path in case.items():
            if not isinstance(path, list) or len(path) != HORIZON:
                raise InputError(f"{name}.{key}: expected exactly {HORIZON} annual inputs")
            for year, raw in enumerate(path, 1):
                value = finite_number(raw, f"{name}.{key}, year {year}")
                if value < -1 or (key == "fx_depreciation" and value == -1):
                    raise InputError(f"{name}.{key}, year {year}: invalid growth rate")


def value_case(config: dict, name: str) -> dict:
    """Discount five end-year dividends plus terminal value in USD per ADS.

    Zero distributions give zero value and zero terminal share by convention.
    Capital requirements and dividend capacity are outside the model's scope.
    """
    validate_config(config)
    if name not in CASE_NAMES:
        raise InputError(f"Unknown case: {name}")
    ke = cost_of_equity(config)
    growth_usd = terminal_usd_growth(config)
    dividend_kzt = config["quarterly_dividend_assumption_kzt"] * 4
    fx = config["fx_reference_kzt_per_usd"]
    case = config["cases"][name]
    cashflows = []
    for year, (growth, depreciation) in enumerate(
        zip(case["dividend_growth"], case["fx_depreciation"]), 1
    ):
        dividend_kzt *= 1 + growth
        fx *= 1 + depreciation
        dividend_usd = dividend_kzt / fx
        cashflows.append({"year": year, "dividend_kzt": dividend_kzt,
                          "fx_kzt_per_usd": fx, "dividend_usd": dividend_usd,
                          "present_value_usd": dividend_usd / (1 + ke) ** year})
    explicit_pv = math.fsum(row["present_value_usd"] for row in cashflows)
    terminal_pv = (cashflows[-1]["dividend_usd"] * (1 + growth_usd)
                   / (ke - growth_usd) / (1 + ke) ** HORIZON)
    value = explicit_pv + terminal_pv
    if not math.isfinite(value):
        raise InputError("Scenario exceeds the supported numerical range")
    return {"value_usd": value, "terminal_share": terminal_pv / value if value else 0.0,
            "explicit_pv_usd": explicit_pv, "terminal_pv_usd": terminal_pv,
            "cost_of_equity": ke, "terminal_usd_growth": growth_usd,
            "cashflows": cashflows}


def earnings_sensitivity(config: dict) -> dict:
    """Static one-year expense shocks in KZT billions, before behavioural effects."""
    validate_config(config)
    funding = config["average_savings_kzt_bn"] * config["funding_shock"]
    credit = config["average_net_loans_kzt_bn"] * config["credit_shock"]
    after_tax = (funding + credit) * (1 - config["tax_assumption"])
    return {"funding_expense_kzt_bn": funding, "credit_loss_expense_kzt_bn": credit,
            "pretax_stress_kzt_bn": funding + credit,
            "after_tax_stress_kzt_bn": after_tax,
            "stress_fraction_annualised_h1_income":
                after_tax / (2 * config["h1_group_net_income_kzt_bn"])}


def analyse_segments(csv_path: Path, sql_path: Path, controls: dict) -> list[dict]:
    """Require a complete two-year panel and independent group-income controls."""
    expected_keys = {(year, name) for year in (2024, 2025) for name in SEGMENTS}
    rows, seen = [], set()
    with csv_path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["year", "segment", "revenue_kzt_mn", "net_income_kzt_mn"]:
            raise InputError("Segment CSV columns do not match the documented schema")
        for line, row in enumerate(reader, 2):
            try:
                year, name = int(row["year"]), row["segment"]
                revenue = finite_number(float(row["revenue_kzt_mn"]), f"Revenue, line {line}")
                income = finite_number(float(row["net_income_kzt_mn"]), f"Income, line {line}")
            except (TypeError, ValueError) as exc:
                raise InputError(f"Invalid segment data on line {line}: {exc}") from exc
            key = (year, name)
            if key not in expected_keys or key in seen or revenue < 0:
                raise InputError(f"Unexpected/duplicate segment-year or negative revenue: {key}")
            seen.add(key)
            rows.append((year, name, revenue, income))
    if seen != expected_keys:
        raise InputError(f"Missing segment-years: {sorted(expected_keys-seen)}")
    for year in (2024, 2025):
        expected = finite_number(controls[str(year)], f"Group income control {year}")
        actual = math.fsum(row[3] for row in rows if row[0] == year)
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=0.001):
            raise InputError(f"Segment income does not reconcile for {year}: {actual} vs {expected}")
    with sqlite3.connect(":memory:") as database:
        database.row_factory = sqlite3.Row
        database.execute("CREATE TABLE segments(year INTEGER, segment TEXT, revenue REAL, "
                         "net_income REAL, PRIMARY KEY(year, segment))")
        database.executemany("INSERT INTO segments VALUES(?, ?, ?, ?)", rows)
        return [dict(row) for row in database.execute(sql_path.read_text(encoding="utf-8"))]


def calculate(config: dict, csv_path: Path, sql_path: Path, controls: dict) -> dict:
    result = {name: value_case(config, name) for name in CASE_NAMES}
    result.update(earnings_sensitivity(config))
    result["as_of"] = config["as_of"]
    result["pe_crosscheck_usd"] = (config["diluted_eps_2025_kzt"]
                                    / config["fx_reference_kzt_per_usd"] * config["pe_assumption"])
    result["segment_analysis"] = analyse_segments(csv_path, sql_path, controls)
    return result


def verify_reference(result: dict, reference: dict) -> None:
    """Optional regression for supplied assumptions; not a live Excel calculation."""
    for name in CASE_NAMES:
        if not math.isclose(result[name]["value_usd"], reference[name], rel_tol=1e-10):
            raise InputError(f"Reference mismatch for {name}; use the original assumptions "
                             "for this check, or run without --verify-reference")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, default=ROOT / "data/assumptions.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/results.json")
    parser.add_argument("--verify-reference", action="store_true",
                        help="Check the distributed baseline against reference values")
    args = parser.parse_args(argv)
    try:
        config = load_json(args.assumptions)
        result = calculate(config, ROOT / "data/segments.csv", ROOT / "sql/segment_analysis.sql",
                           load_json(ROOT / "data/group_income_controls.json"))
        if args.verify_reference:
            verify_reference(result, load_json(ROOT / "data/reference_outputs.json"))
        encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0
    except (InputError, OSError, ValueError, KeyError, ArithmeticError, sqlite3.Error) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
