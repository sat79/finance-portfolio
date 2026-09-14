"""Independently reproduce saved DCF/RI calculations; does not run Excel."""
import argparse
import math
from pathlib import Path

from xlsx_values import read_xlsx

ROOT = Path(__file__).resolve().parents[1]


def verify(path: Path) -> dict:
    workbook = read_xlsx(path)
    comparisons = 0

    def number(sheet, cell):
        value = workbook[sheet][cell]["value"]
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"Missing/non-numeric input at {sheet}!{cell}")
        return value

    def close(sheet, cell, expected):
        nonlocal comparisons
        actual = number(sheet, cell)
        if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-9):
            raise ValueError(f"Mismatch at {sheet}!{cell}: {actual} vs {expected}")
        if not workbook[sheet][cell]["formula"]:
            raise ValueError(f"Expected formula at {sheet}!{cell}")
        comparisons += 1

    d = lambda cell: number("DCF", cell)
    ri = lambda cell: number("Residual_Income", cell)
    ke = d("B45") + d("B46") * d("B47")
    wacc_calculated = ke * (1 - d("B50")) + d("B49") * (1 - d("B7")) * d("B50")
    close("DCF", "B48", ke)
    close("DCF", "B51", wacc_calculated)
    if d("B53") not in (0, 1):
        raise ValueError("Invalid WACC switch")
    wacc = wacc_calculated if d("B53") else d("B52")
    if wacc <= d("B11") or d("B14") <= 0:
        raise ValueError("Invalid discount, terminal growth or share count")
    close("DCF", "B10", wacc)
    revenue = d("B6")
    cashflows = []
    for year, column in enumerate("DEFGH", 1):
        prior_revenue = revenue
        revenue *= 1 + d(f"{column}18")
        ebit = revenue * d(f"{column}20")
        nopat = ebit * (1 - d("B7"))
        depreciation = revenue * d("B8")
        capex = revenue * d(f"{column}25")
        working_capital = (revenue - prior_revenue) * d("B9")
        fcff = nopat + depreciation - capex - working_capital
        for row, expected in {19: revenue, 21: ebit, 22: nopat, 24: depreciation,
                              26: capex, 27: working_capital, 28: fcff}.items():
            close("DCF", f"{column}{row}", expected)
        cashflows.append(fcff)
    explicit_pv = sum(cf / (1 + wacc) ** year for year, cf in enumerate(cashflows, 1))
    terminal_pv = cashflows[-1] * (1 + d("B11")) / (wacc - d("B11")) / (1 + wacc) ** 5
    ev = explicit_pv + terminal_pv
    equity = ev - d("B12") - d("B13")
    dcf = equity / d("B14")
    for cell, expected in {"B33": explicit_pv, "B35": terminal_pv, "B36": ev,
                           "B39": equity, "B41": dcf, "B55": terminal_pv / ev,
                           "I35": dcf, "B56": 0}.items():
        close("DCF", cell, expected)
    # Independent valuation for every sensitivity header combination.
    for row in range(33, 38):
        g = d(f"F{row}")
        for column in "GHIJK":
            rate = d(f"{column}32")
            pv = sum(cf / (1 + rate) ** yr for yr, cf in enumerate(cashflows, 1))
            pv += cashflows[-1] * (1 + g) / (rate - g) / (1 + rate) ** 5
            close("DCF", f"{column}{row}", (pv - d("B12") - d("B13")) / d("B14"))
    book = ri("B5") / ri("B6")
    start_book, eps, ke_ri = book, ri("B8"), ri("B9")
    residuals = []
    for column in "DEFGH":
        eps *= 1 + ri(f"{column}14")
        charge = book * ke_ri
        residual = eps - charge
        end_book = book + eps * (1 - ri(f"{column}19"))
        for row, expected in {15: eps, 16: book, 17: charge, 18: residual, 20: end_book}.items():
            close("Residual_Income", f"{column}{row}", expected)
        residuals.append(residual)
        book = end_book
    ri_pv = sum(cf / (1 + ke_ri) ** yr for yr, cf in enumerate(residuals, 1))
    ri_terminal_pv = residuals[-1] * (1 + ri("B10")) / (ke_ri - ri("B10")) / (1 + ke_ri) ** 5
    ri_value = start_book + ri_pv + ri_terminal_pv
    close("Residual_Income", "B28", ri_value)
    weights = [number("Summary", f"B{row}") for row in (8, 9, 10)]
    if min(weights) < 0 or not math.isclose(sum(weights), 1, abs_tol=1e-9):
        raise ValueError("Invalid method weights")
    weighted = sum(weight * number("Summary", f"C{row}") for row, weight in zip((8, 9, 10), weights))
    close("Summary", "D3", weighted)
    result = {"comparisons": comparisons, "dcf_eur_per_share": dcf,
              "residual_income_eur_per_share": ri_value, "terminal_ev_share": terminal_pv / ev}
    print(f"PASS: {comparisons} saved formula values reproduce independently.")
    print("No cached formula errors. This does not validate historical sources, peer assumptions or native Excel behaviour.")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "models/Unilever-Valuation-Reviewed.xlsx")
    verify(parser.parse_args().workbook)
