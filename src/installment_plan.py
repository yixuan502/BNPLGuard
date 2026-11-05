"""Cent-exact monthly instalment allocation, independent of the simulator."""
from decimal import Decimal, InvalidOperation
from numbers import Integral, Real

def amount(value):
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise ValueError("Enter a finite nonnegative amount in whole cents.")
    try: d = Decimal(str(value))
    except InvalidOperation: raise ValueError("Invalid amount.") from None
    if not d.is_finite() or d < 0 or d * 100 != (d * 100).to_integral_value():
        raise ValueError("Enter a finite nonnegative amount with at most two decimal places.")
    return int(d * 100)

def calculate_plan(purchase, upfront, months):
    total, paid = amount(purchase), amount(upfront)
    if paid > total: raise ValueError("Upfront payment cannot exceed purchase amount.")
    if isinstance(months, bool) or not isinstance(months, Integral) or months < 1:
        raise ValueError("Number of monthly instalments must be a positive integer.")
    remaining = total - paid
    regular = remaining // int(months)
    final = remaining - regular * (int(months) - 1)
    return {"remaining": Decimal(remaining)/100, "regular": Decimal(regular)/100,
            "final": Decimal(final)/100, "maximum": Decimal(max(regular, final))/100,
            "months": int(months)}
