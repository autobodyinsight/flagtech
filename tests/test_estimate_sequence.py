from datetime import datetime

from app.routes.estimate_routes.dashboard_routes import _build_estimate_list_rows


def test_estimate_numbers_start_at_702_in_chronological_order():
    rows = [
        {
            "id": 2,
            "saved_at": "2024-01-02T10:00:00",
            "vehicle": "2023 Honda Civic",
            "owner_info": "Jane Doe",
            "insurance_company": "State Farm",
            "grand_total": "1250.00",
        },
        {
            "id": 1,
            "saved_at": "2024-01-01T12:00:00",
            "vehicle": "2022 Toyota Camry",
            "owner_info": "John Smith",
            "insurance_company": "GEICO",
            "grand_total": "980.50",
        },
    ]

    estimate_list = _build_estimate_list_rows(rows)

    assert [item["estimate_number"] for item in estimate_list] == [702, 703]
    assert estimate_list[0]["vehicle"] == "2022 Toyota Camry"
    assert estimate_list[1]["vehicle"] == "2023 Honda Civic"
    assert estimate_list[0]["customer"] == "John Smith"
    assert estimate_list[1]["customer"] == "Jane Doe"
