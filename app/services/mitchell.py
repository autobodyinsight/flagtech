import re
from typing import Any, Dict, List, Optional


_LABEL_SKIP_LIMIT = 8
_KNOWN_LABELS = (
    "owner",
    "appraiser",
    "insurance company",
    "claim number",
)

_MITCHELL_SUMMARY_TOTAL_LABELS = {
    "taxable parts": "parts_total",
    "gross total": "grand_total",
    "deductible": "deductible",
    "total customer": "customer_pay",
    "net estimate total": "insurance_pay",
}

_MITCHELL_REPAIR_END_MARKERS = (
    "estimate totals",
    "taxable parts",
    "gross total",
    "net estimate total",
    "total customer",
)

_MITCHELL_OPERATION_BLOCKLIST = (
    "total price",
    "printed on",
    "mitchell cloud estimating",
    "taxable parts",
    "gross total",
    "estimate totals",
    "net estimate total",
)

# Tokens that prove a line is NOT a paint/refinish operation even if
# "clear coat" or "refinish" appears in noisy OCR text.
_PAINT_NEGATION_TOKENS = (
    "mechanical",
    "sublet",
    "pre-scan",
    "post-scan",
    "pre scan",
    "post scan",
    "scan",
    "calibration",
)


_VIN_RE = re.compile(r"[A-HJ-NPR-Z0-9]{17}", re.IGNORECASE)


def _group_rows(words: List[Dict[str, Any]], y_thresh: float = 6.0) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item.get("y0", 0) + item.get("y1", 0)) / 2):
        ymid = (word.get("y0", 0) + word.get("y1", 0)) / 2
        placed = False
        for row in rows:
            if abs(row["ymid"] - ymid) <= y_thresh:
                row["words"].append(word)
                row["ymid"] = sum(
                    ((entry.get("y0", 0) + entry.get("y1", 0)) / 2 for entry in row["words"])
                ) / len(row["words"])
                placed = True
                break
        if not placed:
            rows.append({"ymid": ymid, "words": [word]})
    return rows


def _group_row_words_by_x(words: List[Dict[str, Any]], gap: float = 15.0) -> List[Dict[str, Any]]:
    if not words:
        return []

    sorted_words = sorted(words, key=lambda item: item.get("x0", 0))
    groups: List[List[Dict[str, Any]]] = []
    current = [sorted_words[0]]
    for word in sorted_words[1:]:
        previous = current[-1]
        if word.get("x0", 0) - previous.get("x1", 0) > gap:
            groups.append(current)
            current = [word]
        else:
            current.append(word)
    groups.append(current)

    result: List[Dict[str, Any]] = []
    for group in groups:
        result.append(
            {
                "words": group,
                "text": " ".join(item.get("text", "") for item in group).strip(),
                "min_x": min(item.get("x0", 0) for item in group),
            }
        )
    return result


def _row_text(row: Dict[str, Any]) -> str:
    return " ".join(
        word.get("text", "") for word in sorted(row.get("words", []), key=lambda item: item.get("x0", 0))
    ).strip()


def _text_in_bounds(row: Dict[str, Any], left_bound: float, right_bound: Optional[float]) -> str:
    filtered_words = [
        word
        for word in row.get("words", [])
        if word.get("xmid", 0) >= left_bound and (right_bound is None or word.get("xmid", 0) < right_bound)
    ]
    return " ".join(
        word.get("text", "") for word in sorted(filtered_words, key=lambda item: item.get("x0", 0))
    ).strip()


def _normalize_line_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _is_label_only_value(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", str(text or "").strip().lower())
    if not lowered:
        return True
    return any(label in lowered and ":" in lowered for label in _KNOWN_LABELS)


def _extract_value_below_label(pages: List[Dict[str, Any]], label: str) -> str:
    label_lower = label.lower()

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for idx, row in enumerate(rows):
            groups = _group_row_words_by_x(row.get("words", []))
            target_index = None
            for group_index, group in enumerate(groups):
                normalized_text = re.sub(r"\s+", " ", group.get("text", "").strip().lower())
                if label_lower in normalized_text:
                    target_index = group_index
                    break

            if target_index is None:
                continue

            target_group = groups[target_index]
            left_bound = target_group["min_x"] - 2
            right_bound = None
            if target_index + 1 < len(groups):
                right_bound = groups[target_index + 1]["min_x"] - 2

            scan_end = min(len(rows), idx + 1 + _LABEL_SKIP_LIMIT)
            for next_idx in range(idx + 1, scan_end):
                candidate_text = _text_in_bounds(rows[next_idx], left_bound, right_bound)
                if not candidate_text:
                    continue
                if _is_label_only_value(candidate_text):
                    continue
                return candidate_text

    return ""


def _extract_vehicle_header_line(pages: List[Dict[str, Any]]) -> str:
    exterior_color_pattern = re.compile(r"exterior\s+color", re.IGNORECASE)

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for idx, row in enumerate(rows):
            if exterior_color_pattern.search(_row_text(row)):
                for prev_idx in range(idx - 1, max(-1, idx - 6), -1):
                    candidate = _row_text(rows[prev_idx])
                    if re.match(r"^\d{4}\b", candidate):
                        return candidate
                break

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for row in rows:
            candidate = _row_text(row)
            if re.match(r"^\d{4}\b", candidate):
                return candidate
    return ""


def _parse_vehicle_header_fields(vehicle_line: str) -> tuple[str, str, str]:
    cleaned = str(vehicle_line or "").strip()
    if not cleaned:
        return "", "", ""

    match = re.match(r"^(\d{4})\b\s+(\S+)\s+(\S+)", cleaned)
    if not match:
        return "", "", ""

    return match.group(1), match.group(2), match.group(3)


def _extract_vin(pages: List[Dict[str, Any]]) -> str:
    raw = _extract_value_below_label(pages, "VIN")
    if not raw:
        return ""
    match = _VIN_RE.search(raw)
    return match.group(0).upper() if match else ""


def _to_float(value: str) -> Optional[float]:
    text = str(value or "").strip()
    if not text:
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", text)
    if not cleaned or cleaned in {"-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except Exception:
        return None


def _parse_last_money_value(text: str) -> Optional[float]:
    source = str(text or "")
    if not source:
        return None

    money_with_cents = re.findall(r"\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})", source)
    if money_with_cents:
        return _to_float(money_with_cents[-1])

    dollar_values = re.findall(r"\$\s*\d+(?:,\d{3})*(?:\.\d{1,2})?", source)
    if dollar_values:
        return _to_float(dollar_values[-1])

    return None


def _row_money_values(row: Dict[str, Any]) -> List[float]:
    values: List[float] = []
    for word in sorted(row.get("words", []), key=lambda item: item.get("x0", 0)):
        parsed = _to_float(str(word.get("text", "")))
        if parsed is not None:
            values.append(parsed)
    return values


def _normalize_header_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9#]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _repair_header_key(text: str) -> Optional[str]:
    normalized = _normalize_header_text(text)
    if not normalized:
        return None
    if "line" in normalized:
        return "line_num"
    if "operation" in normalized or normalized in {"oper", "op"}:
        return "operation"
    if "description" in normalized or normalized.startswith("desc"):
        return "description"
    if normalized == "type":
        return "type"
    if "number" in normalized:
        return "part_number"
    if normalized in {"qty", "quantity"}:
        return "qty"
    if "total units" in normalized or normalized == "units":
        return "total_units"
    if (
        "extended price" in normalized
        or "ext price" in normalized
        or "total price" in normalized
        or normalized == "price"
    ):
        return "total_price"
    return None


def _detect_repair_columns(row: Dict[str, Any]) -> Dict[str, tuple[float, Optional[float]]]:
    groups = _group_row_words_by_x(row.get("words", []), gap=14.0)
    selected: Dict[str, Dict[str, float]] = {}
    type_seen = 0
    for group in groups:
        raw_text = group.get("text", "")
        normalized = _normalize_header_text(raw_text)
        key = _repair_header_key(raw_text)
        if normalized == "type":
            type_seen += 1
            key = "type" if type_seen == 1 else "part_type"

        if not key:
            continue
        if key in selected:
            continue
        selected[key] = {"min_x": float(group.get("min_x", 0.0))}

    # Mitchell OCR is noisy; keep only core required headers and treat others as optional.
    required = {"line_num", "operation", "type"}
    if not required.issubset(selected.keys()):
        return {}

    ordered = sorted(selected.items(), key=lambda item: item[1]["min_x"])
    ranges: Dict[str, tuple[float, Optional[float]]] = {}
    for index, (key, bounds) in enumerate(ordered):
        left = bounds["min_x"] - 2.0
        if index + 1 < len(ordered):
            right = ordered[index + 1][1]["min_x"] - 2.0
        else:
            right = None
        ranges[key] = (left, right)
    return ranges


def _parse_total_units(value: str) -> Optional[float]:
    text = str(value or "").strip()
    if not text:
        return None
    if "INC" in text.upper():
        return None

    number_match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not number_match:
        return None
    return _to_float(number_match.group(0))


def _append_text(base: str, extra: str) -> str:
    base_clean = str(base or "").strip()
    extra_clean = str(extra or "").strip()
    if not extra_clean:
        return base_clean
    if not base_clean:
        return extra_clean
    return f"{base_clean} {extra_clean}"


def _clean_mitchell_description(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()

    # Noise token 1: leading 5-8 digit code.
    cleaned = re.sub(r"^\d{5,8}\b\s*", "", cleaned)
    # Noise token 2: leading standalone AUTO.
    cleaned = re.sub(r"^AUTO\b\s*", "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip(" -")
    return re.sub(r"\s+", " ", cleaned).strip()


def _normalize_mitchell_part_type(text: str) -> str:
    """Normalize raw Mitchell part-type text to a canonical label."""
    t = str(text or "").strip()
    lower = t.lower()
    if not t:
        return "OEM"
    if "recycled" in lower or "lkq" in lower:
        return "LKQ"
    if "aftermarket" in lower or "a/m" in lower:
        return "A/M"
    if "sublet" in lower:
        return "SUBLET"
    return t


def _is_paint_line(operation_text: str, labor_type_text: str, description: str = "") -> bool:
    haystack = f"{operation_text} {labor_type_text} {description}".lower()
    if any(token in haystack for token in _PAINT_NEGATION_TOKENS):
        return False
    paint_tokens = ("refinish", "blend", "clear coat", "clearcoat")
    return any(token in haystack for token in paint_tokens)


def _is_end_of_mitchell_repair_section(row_text: str) -> bool:
    normalized = _normalize_line_text(row_text)
    if not normalized:
        return False
    return any(marker in normalized for marker in _MITCHELL_REPAIR_END_MARKERS)


def _is_valid_mitchell_operation_text(text: str) -> bool:
    value = str(text or "").strip().lower()
    if not value:
        return False
    if not re.search(r"[a-z]", value):
        return False
    if any(token in value for token in _MITCHELL_OPERATION_BLOCKLIST):
        return False
    return True


def _extract_mitchell_repair_lines(pages: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    labor_items: List[Dict[str, Any]] = []
    paint_items: List[Dict[str, Any]] = []
    parts_items: List[Dict[str, Any]] = []

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        row_index = 0
        while row_index < len(rows):
            header_ranges = _detect_repair_columns(rows[row_index])
            if not header_ranges:
                row_index += 1
                continue

            ordered_columns = sorted(header_ranges.items(), key=lambda item: item[1][0])
            ordered_keys = [key for key, _ in ordered_columns]
            current_row: Optional[Dict[str, Any]] = None

            description_fallback_bounds: Optional[tuple[float, Optional[float]]] = None
            if "description" not in header_ranges and "line_num" in header_ranges and "operation" in header_ranges:
                description_fallback_bounds = (
                    header_ranges["line_num"][0],
                    header_ranges["operation"][0],
                )

            def _flush_current_row() -> None:
                if not current_row:
                    return

                line_num_text = str(current_row.get("line_num", ""))
                line_num_match = re.search(r"\b(\d{1,4})\b", line_num_text)
                if not line_num_match:
                    return
                line_num = int(line_num_match.group(1))
                if line_num >= 1000:
                    return
                description = _clean_mitchell_description(current_row.get("description", ""))
                operation_text = str(current_row.get("operation", "")).strip()
                labor_type_text = str(current_row.get("type", "")).strip()
                part_type_text = str(current_row.get("part_type", "")).strip()
                part_number_text = str(current_row.get("part_number", "")).strip()

                total_units = _parse_total_units(current_row.get("total_units", ""))
                qty_value = _to_float(current_row.get("qty", ""))
                total_price = _to_float(current_row.get("total_price", ""))
                if total_price is None:
                    total_price = _parse_last_money_value(current_row.get("row_text", ""))

                if qty_value is not None and qty_value >= 1 and total_price is not None and total_price > 0 and (
                    part_number_text or part_type_text
                ):
                    parts_items.append(
                        {
                            "line": line_num,
                            "description": description,
                            "part_type": _normalize_mitchell_part_type(part_type_text),
                            "part_number": part_number_text,
                            "price": float(total_price),
                            "qty": float(qty_value),
                            "row_text": str(current_row.get("row_text", "")).strip(),
                        }
                    )

                if total_units is None or total_units <= 0:
                    return
                if total_units > 40:
                    return
                if not _is_valid_mitchell_operation_text(operation_text):
                    return

                op_type_prefix = f"[{operation_text}|{labor_type_text}]"
                item = {
                    "line": str(line_num),
                    "description": f"{op_type_prefix} {description}".strip(),
                    "value": float(total_units),
                }

                description_lower = description.lower()
                paint_line = _is_paint_line(operation_text, labor_type_text, description)
                if paint_line:
                    paint_items.append(item)
                    return

                if "add for clear coat" in description_lower:
                    return

                labor_items.append(item)

            cursor = row_index + 1
            while cursor < len(rows):
                row = rows[cursor]
                if _detect_repair_columns(row):
                    break
                if _is_end_of_mitchell_repair_section(_row_text(row)):
                    break

                line_text = _text_in_bounds(row, *header_ranges["line_num"])
                line_match = re.search(r"\b(\d{1,4})\b", line_text)
                row_fields = {
                    key: _text_in_bounds(row, *bounds)
                    for key, bounds in header_ranges.items()
                }
                if "description" not in row_fields and description_fallback_bounds:
                    row_fields["description"] = _text_in_bounds(row, *description_fallback_bounds)
                row_fields["row_text"] = _row_text(row)

                has_any_column_text = any(str(value or "").strip() for value in row_fields.values())

                if line_match:
                    _flush_current_row()
                    row_fields["line_num"] = line_match.group(1)
                    current_row = row_fields
                elif current_row and has_any_column_text:
                    for key in ordered_keys:
                        if key == "line_num":
                            continue
                        current_row[key] = _append_text(current_row.get(key, ""), row_fields.get(key, ""))
                    current_row["row_text"] = _append_text(current_row.get("row_text", ""), row_fields.get("row_text", ""))

                cursor += 1

            _flush_current_row()

            row_index = cursor

    return labor_items, paint_items, parts_items


def _extract_mitchell_estimate_totals(pages: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    totals: Dict[str, Optional[float]] = {
        "parts_total": None,
        "grand_total": None,
        "deductible": None,
        "customer_pay": None,
        "insurance_pay": None,
        "body_labor": None,
        "paint_labor": None,
        "frame_labor": None,
        "mechanical_labor": None,
        "glass_labor": None,
    }

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for row in rows:
            line_text = _row_text(row)
            normalized_line = _normalize_line_text(line_text)
            if not normalized_line:
                continue

            for label, schema_key in _MITCHELL_SUMMARY_TOTAL_LABELS.items():
                if totals[schema_key] is not None:
                    continue
                if label not in normalized_line:
                    continue
                value = _parse_last_money_value(line_text)
                if value is None:
                    monies = _row_money_values(row)
                    value = monies[-1] if monies else None
                totals[schema_key] = value

    return totals


def parse_mitchell(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    for page_index, page in enumerate(pages, start=1):
        for word in page.get("words", []):
            word.setdefault("page_index", page_index)
            word.setdefault("xmid", (word.get("x0", 0) + word.get("x1", 0)) / 2.0)
            word.setdefault("ymid", (word.get("y0", 0) + word.get("y1", 0)) / 2.0)

    owner_info = _extract_value_below_label(pages, "owner")
    estimator = _extract_value_below_label(pages, "appraiser")
    insurance_company = _extract_value_below_label(pages, "insurance company")
    claim_number = _extract_value_below_label(pages, "claim number")
    vehicle_info_line = _extract_vehicle_header_line(pages)
    year, make, model = _parse_vehicle_header_fields(vehicle_info_line)
    vin = _extract_vin(pages)
    labor_items, paint_items, parts_items = _extract_mitchell_repair_lines(pages)
    totals = _extract_mitchell_estimate_totals(pages)

    return {
        "labor_items": labor_items,
        "paint_items": paint_items,
        "parts_items": parts_items,
        "total_labor": sum(float(item.get("value", 0.0) or 0.0) for item in labor_items),
        "total_paint": sum(float(item.get("value", 0.0) or 0.0) for item in paint_items),
        "first_ro_line": "",
        "second_ro_line": "",
        "vehicle_info_line": vehicle_info_line,
        "owner": owner_info,
        "owner_info": owner_info,
        "insurance_company": insurance_company,
        "written_by": "",
        "estimator": estimator,
        "vin": vin,
        "claim": claim_number,
        "claim_number": claim_number,
        "year": year,
        "make": make,
        "model": model,
        "anchor_page": None,
        "anchor_ymid": None,
        "subtotals_page": None,
        "subtotals_ymid": None,
        "parts_total": totals.get("parts_total"),
        "grand_total": totals.get("grand_total"),
        "deductible": totals.get("deductible"),
        "customer_pay": totals.get("customer_pay"),
        "insurance_pay": totals.get("insurance_pay"),
        "body_labor": totals.get("body_labor"),
        "paint_labor": totals.get("paint_labor"),
        "frame_labor": totals.get("frame_labor"),
        "mechanical_labor": totals.get("mechanical_labor"),
        "glass_labor": totals.get("glass_labor"),
    }
