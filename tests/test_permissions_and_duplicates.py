from app.services.duplicates import duplicate_reason, find_duplicates, name_key
from app.services.permissions import ACCESS_ARCHITECT, build_permission_snapshot, snapshot_can_view_financials
from app.services.vehicle_diagram import area_catalog, render_vehicle_svg


def _snapshot(role, architect=False):
    return build_permission_snapshot(
        role=role,
        domain="autobodyinsight.com",
        shop_id=1,
        shop_uuid="00000000-0000-0000-0000-000000000001",
        user_uuid="00000000-0000-0000-0000-000000000002",
        is_architect=architect,
    )


def test_architect_keeps_full_access_even_if_role_looks_limited():
    snapshot = _snapshot("Tech", architect=True)
    assert snapshot["access_level"] == ACCESS_ARCHITECT
    assert snapshot["features"]["reports"] is True
    assert snapshot["features"]["payments"] is True
    assert snapshot_can_view_financials(snapshot) is True


def test_existing_non_tech_roles_keep_access():
    for role in ("Manager", "Estimator", "Receptionist", "HR", "Support", "Owner", "Front Office"):
        snapshot = _snapshot(role)
        assert snapshot["features"]["reports"] is True, role
        assert snapshot["features"]["payments"] is True, role
        assert snapshot_can_view_financials(snapshot) is True


def test_tech_cannot_see_financials():
    for role in ("Tech", "Technician"):
        snapshot = _snapshot(role)
        assert snapshot["features"]["dashboard"] is True
        assert snapshot["features"]["reports"] is False
        assert snapshot["features"]["payments"] is False
        assert snapshot_can_view_financials(snapshot) is False


def test_duplicate_customer_name_order_and_vin():
    existing = {"ro": "15151515", "vin": "1FT1234567890ABCD", "year": "2024", "make": "Ford", "model": "Maverick", "customer": "DOE JOHN"}
    same_name = {"ro": "17181920", "vin": "", "year": "2024", "make": "Ford", "model": "Maverick", "customer": "JOHN DOE"}
    same_vin = {"ro": "999", "vin": "1ft1234567890abcd", "year": "", "make": "", "model": "", "customer": "Someone Else"}
    assert name_key("DOE JOHN") == name_key("JOHN DOE")
    assert duplicate_reason(existing, same_name) == "same customer and vehicle"
    assert duplicate_reason(existing, same_vin) == "same VIN"
    assert find_duplicates([existing], {"ro": "15151515", "vin": existing["vin"], "customer": "DOE JOHN"}) == []


def test_diagram_adapts_to_body_and_doors():
    coupe = area_catalog("coupe", 2)
    ids = {item["id"] for item in coupe}
    assert "rear_door_l" not in ids
    assert "front_door_l" in ids
    pickup = area_catalog("pickup", 4)
    assert any("bedside" in item["label"] for item in pickup)
    svg = render_vehicle_svg("sedan", 4, "left", "hood")
    assert "data-area=\"hood\"" in svg
    assert "ccc" not in svg.lower()
    assert "<svg" in svg
