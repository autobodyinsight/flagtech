import re
from typing import Any, Dict, List, Optional


_LABEL_SKIP_LIMIT = 8
_KNOWN_LABELS = (
    "owner",
    "appraiser",
    "insurance company",
    "claim number",
)

_REFINISH_OPERATION_KEYWORDS = (
    "refinish",
    "blend",
)

_PART_TYPE_KEYWORDS = (
    "new",
    "qual recycled",
    "aftermarket",
    "sublet",
)

_REPAIR_TABLE_STOP_MARKERS = (
    "subtotal",
    "totals",
    "total loss",
    "summary",
)


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

    grouped: List[Dict[str, Any]] = []
    for group in groups:
        grouped.append(
            {
                "words": group,
                "text": " ".join(item.get("text", "") for item in group).strip(),
                "min_x": min(item.get("x0", 0) for item in group),
                "max_x": max(item.get("x1", 0) for item in group),
            }
        )
    return grouped


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
    """Find the vehicle year/make/model line that appears just above 'Exterior Color'."""
    exterior_color_pattern = re.compile(r"exterior\s+color", re.IGNORECASE)

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for idx, row in enumerate(rows):
            if exterior_color_pattern.search(_row_text(row)):
                # Search upward from the Exterior Color label for a 4-digit year
                for prev_idx in range(idx - 1, max(-1, idx - 6), -1):
                    candidate = _row_text(rows[prev_idx])
                    if re.match(r"^\d{4}\b", candidate):
                        return candidate
                break  # Found the label on this page; no need to keep searching

    # Fallback: first row starting with a 4-digit year anywhere
    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for row in rows:
            row_text = _row_text(row)
            if re.match(r"^\d{4}\b", row_text):
                return row_text
    return ""


_VIN_RE = re.compile(r"[A-HJ-NPR-Z0-9]{17}", re.IGNORECASE)


def _extract_vin(pages: List[Dict[str, Any]]) -> str:
    """Extract the 17-character VIN that appears below the 'VIN' column header."""
    raw = _extract_value_below_label(pages, "VIN")
    if raw:
        match = _VIN_RE.search(raw)
        if match:
            return match.group(0).upper()
    return ""


def _parse_vehicle_header_fields(vehicle_line: str) -> tuple[str, str, str]:
    cleaned = str(vehicle_line or "").strip()
    if not cleaned:
        return "", "", ""

    match = re.match(r"^(\d{4})\b\s+(\S+)\s+(\S+)", cleaned)
    if not match:
        return "", "", ""

    return match.group(1), match.group(2), match.group(3)


def _normalize_header_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9#]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _is_repair_header_row(row: Dict[str, Any]) -> bool:
    text = _normalize_header_text(_row_text(row))
    if not text:
        return False
    has_required = (
        "line" in text
        and "description" in text
        and "operation" in text
        and "qty" in text
        and "type" in text
        and "number" in text
    )
    has_pricing = "price" in text or "tax" in text
    return has_required and has_pricing


def _header_group_key(text: str) -> Optional[str]:
    normalized = _normalize_header_text(text)
    if not normalized:
        return None
    if "line" in normalized:
        return "line"
    if "description" in normalized:
        return "description"
    if "operation" in normalized:
        return "operation_type"
    if "total units" in normalized or normalized == "units" or "units" in normalized:
        return "total_units"
    if normalized == "type":
        return "type"
    if "number" in normalized or normalized in {"part #", "part no", "part number"}:
        return "number"
    if normalized in {"qty", "quantity"} or "qty" in normalized:
        return "qty"
    if "total price" in normalized or normalized == "price" or "price" in normalized:
        return "total_price"
    if "tax" in normalized:
        return "tax"
    return None


def _detect_repair_header_columns(row: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    groups = _group_row_words_by_x(row.get("words", []), gap=14.0)
    selected: Dict[str, Dict[str, float]] = {}
    for group in groups:
        key = _header_group_key(group.get("text", ""))
        if not key:
            continue
        if key in selected:
            continue
        selected[key] = {
            "min_x": float(group.get("min_x", 0.0)),
            "max_x": float(group.get("max_x", 0.0)),
        }

    # Require core columns before attempting extraction.
    required = {"line", "description", "operation_type", "total_units"}
    if not required.issubset(selected.keys()):
        return {}
    return selected


def _build_column_ranges(columns: Dict[str, Dict[str, float]]) -> Dict[str, tuple[float, Optional[float]]]:
    ordered = sorted(columns.items(), key=lambda item: item[1].get("min_x", 0.0))
    ranges: Dict[str, tuple[float, Optional[float]]] = {}
    for index, (key, bounds) in enumerate(ordered):
        left = float(bounds.get("min_x", 0.0)) - 2.0
        if index + 1 < len(ordered):
            right = float(ordered[index + 1][1].get("min_x", 0.0)) - 2.0
        else:
            right = None
        ranges[key] = (left, right)
    return ranges


def _extract_row_field(row: Dict[str, Any], ranges: Dict[str, tuple[float, Optional[float]]], key: str) -> str:
    bounds = ranges.get(key)
    if not bounds:
        return ""
    left, right = bounds
    return _text_in_bounds(row, left, right)


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


def _extract_line_number(value: str) -> str:
    match = re.search(r"\b(\d{1,4})\b", str(value or ""))
    return match.group(1) if match else ""


def _extract_part_number(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    return text


def _extract_description(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    # Mitchell rows can prepend internal numeric tokens before the true part description.
    text = re.sub(r"^\d{4,}\s+", "", text)
    return text


def _is_refinish_operation(operation_type: str) -> bool:
    op = str(operation_type or "").lower()
    return any(keyword in op for keyword in _REFINISH_OPERATION_KEYWORDS)


def _is_parts_replacement(part_type: str) -> bool:
    part_type_lower = str(part_type or "").lower()
    return any(keyword in part_type_lower for keyword in _PART_TYPE_KEYWORDS)


def _is_repair_table_stop_row(row_text: str) -> bool:
    lowered = str(row_text or "").strip().lower()
    if not lowered:
        return False
    return any(marker in lowered for marker in _REPAIR_TABLE_STOP_MARKERS)


def _extract_mitchell_repair_lines(pages: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    labor_items: List[Dict[str, Any]] = []
    paint_items: List[Dict[str, Any]] = []
    parts_items: List[Dict[str, Any]] = []
    seen_rows: set[tuple[str, str, str, str, str, str, str]] = set()

    for page in pages:
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        row_index = 0
        while row_index < len(rows):
            row = rows[row_index]
            if not _is_repair_header_row(row):
                row_index += 1
                continue

            columns = _detect_repair_header_columns(row)
            if not columns:
                row_index += 1
                continue

            ranges = _build_column_ranges(columns)
            cursor = row_index + 1
            while cursor < len(rows):
                candidate = rows[cursor]
                candidate_text = _row_text(candidate)

                if _is_repair_header_row(candidate):
                    break
                if _is_repair_table_stop_row(candidate_text):
                    break

                line_number = _extract_line_number(_extract_row_field(candidate, ranges, "line"))
                if not line_number:
                    cursor += 1
                    continue

                description = _extract_description(_extract_row_field(candidate, ranges, "description"))
                operation_type = _extract_row_field(candidate, ranges, "operation_type")
                total_units_raw = _extract_row_field(candidate, ranges, "total_units")
                total_units = _to_float(total_units_raw)
                part_type = _extract_row_field(candidate, ranges, "type")
                part_number = _extract_part_number(_extract_row_field(candidate, ranges, "number"))
                qty = _to_float(_extract_row_field(candidate, ranges, "qty"))
                total_price = _to_float(_extract_row_field(candidate, ranges, "total_price"))
                tax_text = _extract_row_field(candidate, ranges, "tax")
                tax = str(tax_text or "").strip().lower() in {"yes", "y", "true", "tax"}

                row_key = (
                    line_number,
                    description,
                    operation_type,
                    part_type,
                    part_number,
                    str(qty if qty is not None else ""),
                    str(total_price if total_price is not None else ""),
                )
                if row_key in seen_rows:
                    cursor += 1
                    continue
                seen_rows.add(row_key)

                if _is_refinish_operation(operation_type):
                    paint_items.append(
                        {
                            "line": line_number,
                            "description": description,
                            "value": total_units if total_units is not None else 0.0,
                            "operation_type": operation_type,
                            "total_units": total_units if total_units is not None else 0.0,
                            "type": part_type,
                            "number": part_number,
                            "qty": qty if qty is not None else 0.0,
                            "total_price": total_price if total_price is not None else 0.0,
                            "tax": tax,
                        }
                    )
                elif _is_parts_replacement(part_type):
                    parts_items.append(
                        {
                            "line": line_number,
                            "description": description,
                            "part_type": part_type,
                            "price": total_price if total_price is not None else 0.0,
                            "qty": qty if qty is not None else 0.0,
                            "operation_type": operation_type,
                            "total_units": total_units if total_units is not None else 0.0,
                            "number": part_number,
                            "tax": tax,
                        }
                    )
                else:
                    labor_items.append(
                        {
                            "line": line_number,
                            "description": description,
                            "value": total_units if total_units is not None else 0.0,
                            "operation_type": operation_type,
                            "total_units": total_units if total_units is not None else 0.0,
                            "type": part_type,
                            "number": part_number,
                            "qty": qty if qty is not None else 0.0,
                            "total_price": total_price if total_price is not None else 0.0,
                            "tax": tax,
                        }
                    )

                cursor += 1

            row_index = cursor

    return labor_items, paint_items, parts_items


def parse_mitchell(words: List[Dict[str, Any]]) -> Dict[str, Any]:
    pages = words
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
    total_labor = sum(float(item.get("value", 0.0) or 0.0) for item in labor_items)
    total_paint = sum(float(item.get("value", 0.0) or 0.0) for item in paint_items)
    parts_total = sum(float(item.get("price", 0.0) or 0.0) for item in parts_items) if parts_items else None

    return {
        "labor_items": labor_items,
        "paint_items": paint_items,
        "parts_items": parts_items,
        "total_labor": total_labor,
        "total_paint": total_paint,
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
        "parts_total": parts_total,
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