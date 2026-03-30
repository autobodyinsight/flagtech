from app.services.mitchell import parse_mitchell


HEADER_COLUMNS = {
    "line_num": 20,
    "description": 120,
    "operation": 460,
    "type": 610,
    "total_units": 760,
    "part_type": 900,
    "part_number": 1060,
    "qty": 1220,
    "total_price": 1320,
}


def _make_cell_words(text: str, x_start: float, y: float):
    words = []
    cursor = x_start
    for token in str(text or "").split():
        width = max(12.0, float(len(token) * 7))
        words.append({"text": token, "x0": cursor, "x1": cursor + width, "y0": y, "y1": y + 8})
        cursor += width + 4
    return words


def _make_repair_page(rows):
    words = []

    header = {
        "line_num": "Line #",
        "description": "Description",
        "operation": "Operation",
        "type": "Type",
        "total_units": "Total Units",
        "part_type": "Type",
        "part_number": "Number",
        "qty": "Qty",
        "total_price": "Total Price",
    }

    y = 100.0
    for key, value in header.items():
        words.extend(_make_cell_words(value, HEADER_COLUMNS[key], y))

    y += 14.0
    for row in rows:
        for key, value in row.items():
            if key not in HEADER_COLUMNS:
                continue
            words.extend(_make_cell_words(value, HEADER_COLUMNS[key], y))
        y += 14.0

    return {"width": 1600, "height": 1200, "words": words}


def test_parts_item_from_row_with_inc_units_and_wrapped_continuation():
    page = _make_repair_page(
        [
            {
                "line_num": "2",
                "description": "102116 Frt Bumper Cover",
                "operation": "Remove /",
                "type": "Body",
                "total_units": "INC#",
                "part_type": "Aftermarket",
                "part_number": "GM1014122",
                "qty": "1",
                "total_price": "$464.00",
            },
            {
                "operation": "Replace New",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert len(parsed["parts_items"]) == 1
    part = parsed["parts_items"][0]
    assert part["line"] == 2
    assert part["description"] == "Frt Bumper Cover"
    assert part["part_type"] == "A/M"
    assert part["part_number"] == "GM1014122"
    assert part["price"] == 464.0
    assert part["qty"] == 1.0
    assert "row_text" in part
    assert all(item["line"] != "2" for item in parsed["labor_items"])
    assert all(item["line"] != "2" for item in parsed["paint_items"])


def test_paint_item_parses_units_with_suffix_and_noise_cleanup():
    page = _make_repair_page(
        [
            {
                "line_num": "36",
                "description": "101605 L Frt Door Outside",
                "operation": "Blend",
                "type": "Refinish",
                "total_units": "0.9 C",
                "part_type": "Existing",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert parsed["paint_items"] == [
        {
            "line": "36",
            "description": "[Blend|Refinish] L Frt Door Outside",
            "value": 0.9,
        }
    ]


def test_auto_clear_coat_refinish_is_paint_item():
    page = _make_repair_page(
        [
            {
                "line_num": "46",
                "description": "AUTO Clear Coat",
                "operation": "Additional",
                "type": "Refinish",
                "total_units": "2.8",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert parsed["paint_items"] == [
        {
            "line": "46",
            "description": "[Additional|Refinish] Clear Coat",
            "value": 2.8,
        }
    ]


def test_refinish_row_with_wrapped_part_type_and_clear_coat_labor_exclusion():
    page = _make_repair_page(
        [
            {
                "line_num": "34",
                "description": "AUTO Radiator Support Complete",
                "operation": "Refinish",
                "type": "Refinish",
                "total_units": "1.5",
                "part_type": "Existing",
            },
            {
                "part_type": "Only",
            },
            {
                "line_num": "50",
                "description": "Add for clear coat",
                "operation": "Repair",
                "type": "Body",
                "total_units": "1.2",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert {
        "line": "34",
        "description": "[Refinish|Refinish] Radiator Support Complete",
        "value": 1.5,
    } in parsed["paint_items"]
    assert all(item["line"] != "50" for item in parsed["labor_items"])


def test_header_tolerance_when_desc_abbreviated_and_qty_missing():
    words = []
    y = 100.0

    header = {
        "line_num": "Line #",
        "description": "DESC",
        "operation": "Operation",
        "type": "Type",
        "total_units": "Total Units",
        "part_type": "Type",
        "part_number": "Number",
        "total_price": "Total Price",
    }

    for key, value in header.items():
        words.extend(_make_cell_words(value, HEADER_COLUMNS[key], y))

    y += 14.0
    row = {
        "line_num": "12",
        "description": "AUTO Fender Repair",
        "operation": "Repair",
        "type": "Body",
        "total_units": "2.0",
        "total_price": "$0.00",
    }
    for key, value in row.items():
        words.extend(_make_cell_words(value, HEADER_COLUMNS[key], y))

    page = {"width": 1600, "height": 1200, "words": words}
    parsed = parse_mitchell([page])

    assert parsed["labor_items"] == [
        {
            "line": "12",
            "description": "[Repair|Body] Fender Repair",
            "value": 2.0,
        }
    ]


def test_continuation_text_does_not_corrupt_line_number():
    page = _make_repair_page(
        [
            {
                "line_num": "7",
                "description": "Upper Grille",
                "operation": "Repair",
                "type": "Body",
                "total_units": "1.0",
            },
            {
                # Simulate OCR bleed where continuation text lands in the line-number bounds.
                "line_num": "Grille",
                "description": "Molding",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert parsed["labor_items"] == [
        {
            "line": "7",
            "description": "[Repair|Body] Upper Grille Molding",
            "value": 1.0,
        }
    ]


def test_footer_noise_rows_are_not_parsed_as_labor_lines():
    page = _make_repair_page(
        [
            {
                "line_num": "20",
                "description": "R Fender Assy",
                "operation": "Remove /",
                "type": "Body Install",
                "total_units": "0.3",
            },
            {
                "line_num": "3370",
                "description": "Mountain Rd. 89081",
                "operation": "",
                "type": "Way 98409",
                "total_units": "2667.0",
            },
            {
                "line_num": "602",
                "description": "(Work) #",
                "operation": "Total Price",
                "type": "(Work) prts@performanceradiator.com",
                "total_units": "303.0",
            },
        ]
    )

    parsed = parse_mitchell([page])

    assert parsed["labor_items"] == [
        {
            "line": "20",
            "description": "[Remove /|Body Install] R Fender Assy",
            "value": 0.3,
        }
    ]