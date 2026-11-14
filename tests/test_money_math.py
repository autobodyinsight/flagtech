from decimal import Decimal

from app.services.estimate_math import to_repair_order_documents, total_lines
from app.services.money import cents_to_dollars, dollars_to_cents, gp_from_cents, payment_balance_cents


def test_cents_round_half_up():
    assert dollars_to_cents("10.005") == 1001
    assert dollars_to_cents("10.004") == 1000
    assert cents_to_dollars(199) == Decimal("1.99")


def test_estimate_totals_use_integer_cents():
    rates = {
        "body_rate_cents": 5000,
        "refinish_rate_cents": 5000,
        "mechanical_rate_cents": 6000,
        "frame_rate_cents": 7000,
        "paint_materials_per_hour_cents": 3000,
    }
    lines = [
        {
            "operation": "Replace",
            "part_name": "Hood",
            "part_type": "OEM",
            "quantity": "2",
            "price_cents": 10000,
            "body_hours": "1.5",
            "refinish_hours": "2",
            "mechanical_hours": "0.5",
            "frame_hours": "0",
        },
        {"operation": "Sublet", "part_name": "Alignment", "price_cents": 8900, "quantity": "1"},
    ]
    totals = total_lines(lines, rates, deductible_cents=50000)
    # parts 2 * 10000 = 20000
    # body 1.5 * 5000 = 7500
    # refinish 2 * 5000 = 10000
    # materials 2 * 3000 = 6000
    # mechanical 0.5 * 6000 = 3000
    # sublet 8900
    assert totals["parts_cents"] == 20000
    assert totals["body_labor_cents"] == 7500
    assert totals["refinish_labor_cents"] == 10000
    assert totals["materials_cents"] == 6000
    assert totals["mechanical_labor_cents"] == 3000
    assert totals["sublet_cents"] == 8900
    assert totals["grand_total_cents"] == 20000 + 7500 + 10000 + 6000 + 3000 + 8900
    assert totals["customer_pay_cents"] == 50000
    assert totals["insurance_pay_cents"] == totals["grand_total_cents"] - 50000


def test_gross_profit_and_payment_balance():
    gp = gp_from_cents(10000, 2500)
    assert gp["gp_cents"] == 7500
    assert gp["gp_percent"] == Decimal("75.00")
    balance = payment_balance_cents(10000, 4000, 1000)
    assert balance["balance_cents"] == 5000
    assert balance["paid_cents"] == 5000


def test_estimate_to_ro_documents():
    documents = to_repair_order_documents(
        [
            {
                "operation": "Repair",
                "part_name": "Fender",
                "body_hours": "2.0",
                "refinish_hours": "1.0",
                "price_cents": 0,
            }
        ],
        {"body_rate_cents": 100, "refinish_rate_cents": 100, "mechanical_rate_cents": 0, "frame_rate_cents": 0, "paint_materials_per_hour_cents": 0},
        0,
    )
    assert documents["labor_repairs"][0]["value"] == "2.00"
    assert documents["paint_repairs"][0]["description"].startswith("Repair Fender")
    assert documents["estimate_totals"]["grand_total"] == "3.00"
