"""Estimate line totals and conversion into the existing repair-order JSON shape."""

from __future__ import annotations

from decimal import Decimal

from app.services.money import (
    cents_to_dollars,
    dollars_to_cents,
    money_str,
    quantize_money,
    split_customer_insurance,
    to_decimal,
)


OPERATIONS = ("Repair", "Replace", "R&I", "Refinish", "Blend", "Sublet")
PART_TYPES = ("OEM", "Aftermarket", "Used", "Reman")

DEFAULT_RATES = {
    "body_rate_cents": 0,
    "refinish_rate_cents": 0,
    "mechanical_rate_cents": 0,
    "frame_rate_cents": 0,
    "paint_materials_per_hour_cents": 0,
}


def _hours(value) -> Decimal:
    hours = to_decimal(value)
    if hours < 0:
        return Decimal("0")
    return hours.quantize(Decimal("0.01"))


def _rate_cents(rates: dict, key: str) -> int:
    try:
        return max(0, int(rates.get(key) or 0))
    except (TypeError, ValueError):
        return 0


def _hours_amount_cents(hours: Decimal, rate_cents: int) -> int:
    if hours <= 0 or rate_cents <= 0:
        return 0
    amount = (hours * Decimal(rate_cents)).quantize(Decimal("1"))
    return int(amount)


def normalize_line(raw: dict, index: int = 0) -> dict:
    operation = str(raw.get("operation") or "Repair").strip()
    if operation not in OPERATIONS:
        operation = "Repair"
    part_type = str(raw.get("part_type") or "OEM").strip()
    if part_type not in PART_TYPES:
        part_type = "OEM"
    quantity = to_decimal(raw.get("quantity") or raw.get("qty") or 1)
    if quantity <= 0:
        quantity = Decimal("1")
    quantity = quantity.quantize(Decimal("0.01"))
    price_cents = raw.get("price_cents")
    if price_cents is None and raw.get("price") is not None:
        price_cents = dollars_to_cents(raw.get("price"))
    try:
        price_cents = max(0, int(price_cents or 0))
    except (TypeError, ValueError):
        price_cents = 0
    return {
        "line": int(raw.get("line") or index + 1),
        "area": str(raw.get("area") or "").strip()[:80],
        "operation": operation,
        "part_name": str(raw.get("part_name") or raw.get("description") or "Part").strip()[:180],
        "part_type": part_type,
        "part_number": str(raw.get("part_number") or "").strip()[:64],
        "quantity": format(quantity, "f"),
        "price_cents": price_cents,
        "body_hours": format(_hours(raw.get("body_hours") if raw.get("body_hours") is not None else raw.get("body")), "f"),
        "refinish_hours": format(_hours(raw.get("refinish_hours") if raw.get("refinish_hours") is not None else raw.get("paint")), "f"),
        "mechanical_hours": format(_hours(raw.get("mechanical_hours")), "f"),
        "frame_hours": format(_hours(raw.get("frame_hours")), "f"),
        "notes": str(raw.get("notes") or "").strip()[:500],
    }


def price_line(line: dict, rates: dict | None = None) -> dict:
    rates = rates or DEFAULT_RATES
    normalized = normalize_line(line)
    quantity = to_decimal(normalized["quantity"])
    parts_cents = int((Decimal(normalized["price_cents"]) * quantity).quantize(Decimal("1")))
    if normalized["operation"] == "Sublet":
        # Sublet is a dollar amount, not a parts sale, unless hours were also entered.
        sublet_cents = parts_cents
        parts_cents = 0
    else:
        sublet_cents = 0
        if normalized["operation"] in {"Refinish", "Blend"} and normalized["price_cents"] == 0:
            parts_cents = 0
    body_cents = _hours_amount_cents(to_decimal(normalized["body_hours"]), _rate_cents(rates, "body_rate_cents"))
    refinish_cents = _hours_amount_cents(to_decimal(normalized["refinish_hours"]), _rate_cents(rates, "refinish_rate_cents"))
    mechanical_cents = _hours_amount_cents(to_decimal(normalized["mechanical_hours"]), _rate_cents(rates, "mechanical_rate_cents"))
    frame_cents = _hours_amount_cents(to_decimal(normalized["frame_hours"]), _rate_cents(rates, "frame_rate_cents"))
    materials_cents = _hours_amount_cents(
        to_decimal(normalized["refinish_hours"]),
        _rate_cents(rates, "paint_materials_per_hour_cents"),
    )
    line_total = parts_cents + sublet_cents + body_cents + refinish_cents + mechanical_cents + frame_cents + materials_cents
    normalized.update(
        {
            "parts_cents": parts_cents,
            "sublet_cents": sublet_cents,
            "body_cents": body_cents,
            "refinish_cents": refinish_cents,
            "mechanical_cents": mechanical_cents,
            "frame_cents": frame_cents,
            "materials_cents": materials_cents,
            "line_total_cents": line_total,
        }
    )
    return normalized


def total_lines(lines: list[dict], rates: dict | None = None, deductible_cents: int = 0) -> dict:
    priced = [price_line(line, rates) for line in lines or []]
    keys = (
        "parts_cents",
        "sublet_cents",
        "body_cents",
        "refinish_cents",
        "mechanical_cents",
        "frame_cents",
        "materials_cents",
        "line_total_cents",
    )
    totals = {key: sum(int(line.get(key) or 0) for line in priced) for key in keys}
    grand = totals["line_total_cents"]
    split = split_customer_insurance(grand, deductible_cents)
    body_hours = sum((to_decimal(line["body_hours"]) for line in priced), Decimal("0"))
    refinish_hours = sum((to_decimal(line["refinish_hours"]) for line in priced), Decimal("0"))
    mechanical_hours = sum((to_decimal(line["mechanical_hours"]) for line in priced), Decimal("0"))
    frame_hours = sum((to_decimal(line["frame_hours"]) for line in priced), Decimal("0"))
    return {
        "lines": priced,
        "parts_cents": totals["parts_cents"],
        "sublet_cents": totals["sublet_cents"],
        "body_labor_cents": totals["body_cents"],
        "refinish_labor_cents": totals["refinish_cents"],
        "mechanical_labor_cents": totals["mechanical_cents"],
        "frame_labor_cents": totals["frame_cents"],
        "materials_cents": totals["materials_cents"],
        "grand_total_cents": grand,
        "deductible_cents": max(0, int(deductible_cents or 0)),
        "customer_pay_cents": split["customer_pay_cents"],
        "insurance_pay_cents": split["insurance_pay_cents"],
        "body_hours": format(body_hours, "f"),
        "refinish_hours": format(refinish_hours, "f"),
        "mechanical_hours": format(mechanical_hours, "f"),
        "frame_hours": format(frame_hours, "f"),
        "parts_total": money_str(cents_to_dollars(totals["parts_cents"])),
        "grand_total": money_str(cents_to_dollars(grand)),
        "deductible": money_str(cents_to_dollars(max(0, int(deductible_cents or 0)))),
        "customer_pay": split["customer_pay"],
        "insurance_pay": split["insurance_pay"],
        "body_labor": money_str(cents_to_dollars(totals["body_cents"])),
        "paint_labor": money_str(cents_to_dollars(totals["refinish_cents"] + totals["materials_cents"])),
        "mechanical_labor": money_str(cents_to_dollars(totals["mechanical_cents"])),
        "frame_labor": money_str(cents_to_dollars(totals["frame_cents"])),
        "sublet": money_str(cents_to_dollars(totals["sublet_cents"])),
    }


def to_repair_order_documents(lines: list[dict], rates: dict | None = None, deductible_cents: int = 0) -> dict:
    """Build the labor/paint/parts JSON the existing RO screens already read."""
    summary = total_lines(lines, rates, deductible_cents)
    labor = []
    paint = []
    parts = []
    for line in summary["lines"]:
        description = " ".join(
            part for part in (line["operation"], line["part_name"], line["notes"]) if part
        ).strip()
        body_hours = to_decimal(line["body_hours"]) + to_decimal(line["mechanical_hours"]) + to_decimal(line["frame_hours"])
        refinish_hours = to_decimal(line["refinish_hours"])
        if body_hours > 0 or line["operation"] in {"Repair", "Replace", "R&I"}:
            labor.append(
                {
                    "line": str(line["line"]),
                    "description": description,
                    "operation": line["operation"],
                    "part_number": line["part_number"],
                    "value": format(quantize_money(body_hours), "f"),
                }
            )
        if refinish_hours > 0 or line["operation"] in {"Refinish", "Blend"}:
            paint.append(
                {
                    "line": str(line["line"]),
                    "description": description,
                    "operation": line["operation"],
                    "part_number": line["part_number"],
                    "value": format(quantize_money(refinish_hours), "f"),
                }
            )
        if line["operation"] in {"Replace", "Sublet"} or int(line["price_cents"] or 0) > 0 or int(line["sublet_cents"] or 0) > 0:
            parts.append(
                {
                    "line": line["line"],
                    "description": line["part_name"],
                    "part_type": line["part_type"],
                    "part_number": line["part_number"],
                    "qty": format(to_decimal(line["quantity"]), "f"),
                    "price": money_str(cents_to_dollars(line["price_cents"])),
                    "operation": line["operation"],
                }
            )
    estimate_totals = {
        "parts_total": summary["parts_total"],
        "grand_total": summary["grand_total"],
        "deductible": summary["deductible"],
        "customer_pay": summary["customer_pay"],
        "insurance_pay": summary["insurance_pay"],
        "body_labor": summary["body_labor"],
        "paint_labor": summary["paint_labor"],
        "frame_labor": summary["frame_labor"],
        "mechanical_labor": summary["mechanical_labor"],
        "glass_labor": "0.00",
        "sublet": summary["sublet"],
    }
    return {
        "labor_repairs": labor,
        "paint_repairs": paint,
        "parts_repairs": parts,
        "estimate_totals": estimate_totals,
        "summary": summary,
    }
