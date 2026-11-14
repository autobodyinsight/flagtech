from pathlib import Path

from app.services.illustration_variant import known_variant, render_views_html, select_variant, variant_assets
from app.services.vin import decode_vin

CASES = [
    ({"BodyClass": "Sedan/Saloon", "Doors": "4"}, "sedan_4dr"),
    ({"BodyClass": "Hatchback/Liftback/Notchback", "Doors": "5"}, "hatch_4dr"),
    ({"BodyClass": "Coupe", "Doors": "2"}, "coupe_2dr"),
    ({"BodyClass": "Sport Utility Vehicle [SUV]/Multipurpose Vehicle [MPV]", "Doors": "4"}, "suv_4dr_liftgate"),
    ({"BodyClass": "Sport Utility Vehicle [SUV]/Multipurpose Vehicle [MPV]", "Doors": "2"}, "suv_2dr_liftgate"),
    ({"BodyClass": "Crossover Utility Vehicle [CUV]", "Doors": "5"}, "suv_4dr_liftgate"),
    ({"BodyClass": "Minivan", "Doors": "4"}, "minivan"),
    ({"BodyClass": "Pickup", "BodyCabType": "Regular", "Doors": "2"}, "truck_regular_cab"),
    ({"BodyClass": "Pickup", "BodyCabType": "Extra/Super/Quad/Double/King/Extended", "Doors": "4"}, "truck_extended_cab"),
    ({"BodyClass": "Pickup", "BodyCabType": "Crew/Super Crew/Crew Max", "Doors": "4"}, "truck_crew_cab"),
    ({"BodyClass": "Pickup", "BodyCabType": "Crew/Super Crew/Crew Max", "Series": "F-450 DRW"}, "truck_crew_dually"),
    ({"BodyClass": "Incomplete - Chassis Cab (Double Cab)", "Wheels": "6"}, "truck_crew_dually"),
    ({"BodyClass": "Pickup", "Doors": ""}, "truck_crew_cab"),
    ({"BodyClass": "", "Doors": "2"}, "coupe_2dr"),
    ({"BodyClass": "Motorcycle - Sport", "Doors": ""}, "sedan_4dr"),
]


def test_select_variant_matches_the_reference_cases():
    assert len(CASES) == 15
    for record, expected in CASES:
        assert select_variant(record) == expected


def test_manual_variants_stay_available():
    assert known_variant("suv_4dr_swing") == "suv_4dr_swing"
    assert known_variant("suv_2dr_tailgate") == "suv_2dr_tailgate"
    assert known_variant("not-a-variant") == "sedan_4dr"


def test_render_views_include_webp_jpg_and_both_angles():
    html = render_views_html("minivan")
    assert 'type="image/webp"' in html
    assert "minivan_front34.webp" in html
    assert "minivan_front34.jpg" in html
    assert "minivan_rear34.jpg" in html
    assert html.count('class="stage"') == 2
    assets = variant_assets("truck_crew_dually")
    for view in ("front34", "rear34"):
        for kind in ("jpg", "webp", "overlay"):
            path = assets["views"][view][kind].split("/static/vehicles/")[1]
            assert (Path("app/static/vehicles") / path).is_file()


def test_estimate_template_uses_pencil_views_and_keeps_svg_fallback():
    template = Path("app/templates/native_estimate.html").read_text(encoding="utf-8")
    assert 'id="illustrationVariant"' in template
    assert "image/webp" in template
    assert 'id="diagramFallback"' in template
    assert "data-area" in template
    assert "loadFallback" in template


def test_vin_decode_stores_the_illustration_variant():
    def fake_fetch(_url):
        return {
            "Results": [
                {
                    "Make": "FORD",
                    "Model": "F-450",
                    "ModelYear": "2024",
                    "Series": "F-450 DRW",
                    "BodyClass": "Pickup",
                    "BodyCabType": "Crew/Super Crew/Crew Max",
                    "Doors": "4",
                    "Trim": "Lariat",
                }
            ]
        }

    decoded = decode_vin("1" * 17, fetcher=fake_fetch)
    assert decoded["vehicle"]["illustration_variant"] == "truck_crew_dually"
