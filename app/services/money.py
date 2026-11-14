"""Decimal money helpers.

New estimate documents store money as integer cents. Legacy repair-order
columns stay NUMERIC (already exact). This module never uses binary floats
for arithmetic.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")
ZERO = Decimal("0")


def to_decimal(value, default: str = "0") -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None or value is False:
        return Decimal(default)
    text = str(value).strip().replace("$", "").replace(",", "")
    if text == "":
        return Decimal(default)
    try:
        return Decimal(text)
    except Exception:
        return Decimal(default)


def quantize_money(value) -> Decimal:
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def dollars_to_cents(value) -> int:
    amount = quantize_money(value)
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))


def cents_to_dollars(cents) -> Decimal:
    return (Decimal(int(cents or 0)) / Decimal(100)).quantize(CENT, rounding=ROUND_HALF_UP)


def money_str(value) -> str:
    return format(quantize_money(value), "f")


def gp_amounts(sales, cost) -> dict:
    """Gross profit from dollar amounts. Percent is a Decimal with two places."""
    return gp_from_cents(dollars_to_cents(sales), dollars_to_cents(cost))


def gp_from_cents(sales_cents: int, cost_cents: int) -> dict:
    sales_cents = int(sales_cents or 0)
    cost_cents = int(cost_cents or 0)
    gp_cents = sales_cents - cost_cents
    if sales_cents <= 0:
        percent = ZERO
    else:
        percent = (Decimal(gp_cents) / Decimal(sales_cents) * Decimal(100)).quantize(CENT, rounding=ROUND_HALF_UP)
    return {
        "sales_cents": sales_cents,
        "cost_cents": cost_cents,
        "gp_cents": gp_cents,
        "gp_percent": percent,
        "sales": money_str(cents_to_dollars(sales_cents)),
        "cost": money_str(cents_to_dollars(cost_cents)),
        "gp_dollars": money_str(cents_to_dollars(gp_cents)),
    }


def payment_balance_cents(grand_total_cents: int, insurance_paid_cents: int, customer_paid_cents: int) -> dict:
    grand = int(grand_total_cents or 0)
    insurance = int(insurance_paid_cents or 0)
    customer = int(customer_paid_cents or 0)
    paid = insurance + customer
    balance = grand - paid
    return {
        "grand_total_cents": grand,
        "insurance_paid_cents": insurance,
        "customer_paid_cents": customer,
        "paid_cents": paid,
        "balance_cents": balance,
        "grand_total": money_str(cents_to_dollars(grand)),
        "insurance_paid": money_str(cents_to_dollars(insurance)),
        "customer_paid": money_str(cents_to_dollars(customer)),
        "balance": money_str(cents_to_dollars(balance)),
    }


def split_customer_insurance(grand_total_cents: int, deductible_cents: int) -> dict:
    grand = max(0, int(grand_total_cents or 0))
    deductible = max(0, int(deductible_cents or 0))
    customer = min(grand, deductible)
    insurance = grand - customer
    return {
        "customer_pay_cents": customer,
        "insurance_pay_cents": insurance,
        "customer_pay": money_str(cents_to_dollars(customer)),
        "insurance_pay": money_str(cents_to_dollars(insurance)),
    }
