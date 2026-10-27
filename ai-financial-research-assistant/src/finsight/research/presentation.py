"""Display-only rounding; exact source and calculation records are never changed."""

from decimal import Decimal


def display_number(value, unit):
    number = Decimal(value)
    if not number.is_finite():
        return "Unavailable"
    if unit in {"percent", "percentage points"}:
        shown = f"{number:,.2f}"
        if number and abs(number) < Decimal("0.005"):
            shown = "<0.01" if number > 0 else ">-0.01"
        return shown + ("%" if unit == "percent" else " percentage points")
    for scale, label in [
        (Decimal("1e12"), "trillion"),
        (Decimal("1e9"), "billion"),
        (Decimal("1e6"), "million"),
    ]:
        if abs(number) >= scale:
            return f"{number / scale:,.2f} {label} {unit}"
    return f"{number:,.2f} {unit}"


def display_fact(claim):
    return (
        f"{claim['metric'].replace('_', ' ')}: {display_number(claim['value'], claim['unit'])} "
        f"({claim['period_start'] or 'instant'} to {claim['period_end']}; "
        f"underlying currency {claim['currency']})."
    )
