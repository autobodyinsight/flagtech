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

_DUPLICATE_PARTS_TYPE_KEYWORDS = (
    "new",
    "qual recycled",
    "aftermarket",
)

_NON_LABOR_DESCRIPTION_KEYWORDS = (
    "paint/materials",
    "paint materials",
    "hazardous waste",
)

_REPAIR_TABLE_STOP_MARKERS = (
    "subtotal",
    "totals",
    "total loss",
    "summary",
)

_MITCHELL_TOTALS_HEADER = (
    "labor",
    "units",
    "rate",
    "sublet",
    "addl amount",
    "totals",
)

_MITCHELL_LABOR_TOTAL_LABELS = {
    "body labor": "body_labor",
    "refinish labor": "paint_labor",
    "mechanical labor": "mechanical_labor",
    "frame labor": "frame_labor",
    "glass labor": "glass_labor",
}

_MITCHELL_SUMMARY_TOTAL_LABELS = {
    "taxable parts": "parts_total",
    "gross total": "grand_total",
    "deductible": "deductible",
    "total customer": "customer_pay",
    "net estimate total": "insurance_pay",
}


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
    if (
        "extended price" in normalized
        or "ext price" in normalized
        or "total price" in normalized
        or normalized == "price"
        or "price" in normalized
    ):
        return "ext_price"
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


def _parse_last_money_value(text: str) -> Optional[float]:
    source = str(text or "")
    if not source:
        return None

    # Prefer currency-like values with cents to avoid capturing part numbers.
    money_with_cents = re.findall(r"\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})", source)
    if money_with_cents:
        return _to_float(money_with_cents[-1])

    # Fallback: last dollar-prefixed value (may not include cents).
    dollar_values = re.findall(r"\$\s*\d+(?:,\d{3})*(?:\.\d{1,2})?", source)
    if dollar_values:
        return _to_float(dollar_values[-1])

    return None


def _normalize_cell_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower())
    collapsed = re.sub(r"\s+", " ", cleaned).strip()
    return collapsed.replace("add l", "addl")


def _row_money_values(row: Dict[str, Any]) -> List[float]:
    values: List[float] = []
    for word in sorted(row.get("words", []), key=lambda item: item.get("x0", 0)):
        parsed = _to_float(str(word.get("text", "")))
        if parsed is not None:
            values.append(parsed)
    return values


def _find_mitchell_totals_header_row(rows: List[Dict[str, Any]]) -> Optional[int]:
    for idx, row in enumerate(rows):
        groups = _group_row_words_by_x(row.get("words", []), gap=15.0)
        normalized_groups = [_normalize_cell_text(group.get("text", "")) for group in groups]
        if normalized_groups == list(_MITCHELL_TOTALS_HEADER):
            return idx
    return None


def _extract_totals_table_values(rows: List[Dict[str, Any]], header_index: int) -> Dict[str, Optional[float]]:
    result: Dict[str, Optional[float]] = {
        "body_labor": None,
        "paint_labor": None,
        "mechanical_labor": None,
        "frame_labor": None,
        "glass_labor": None,
    }

    header_groups = _group_row_words_by_x(rows[header_index].get("words", []), gap=15.0)
    if len(header_groups) != len(_MITCHELL_TOTALS_HEADER):
        return result

    ranges: List[tuple[float, Optional[float]]] = []
    for i, group in enumerate(header_groups):
        left = float(group.get("min_x", 0.0)) - 2.0
        if i + 1 < len(header_groups):
            right = float(header_groups[i + 1].get("min_x", 0.0)) - 2.0
        else:
            right = None
        ranges.append((left, right))

    for row in rows[header_index + 1 :]:
        label_text = _normalize_cell_text(_text_in_bounds(row, ranges[0][0], ranges[0][1]))
        if not label_text:
            break

        if label_text in _MITCHELL_SUMMARY_TOTAL_LABELS:
            break

        totals_text = _text_in_bounds(row, ranges[-1][0], ranges[-1][1])
        totals_value = _to_float(totals_text)
        if totals_value is None:
            monies = _row_money_values(row)
            totals_value = monies[-1] if monies else None

        schema_key = _MITCHELL_LABOR_TOTAL_LABELS.get(label_text)
        if schema_key:
            result[schema_key] = totals_value

        # Stop once table rows no longer look like the six-column totals structure.
        row_groups = _group_row_words_by_x(row.get("words", []), gap=15.0)
        if len(row_groups) < len(header_groups) - 1:
            break

    return result


def _extract_summary_totals(rows: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    result: Dict[str, Optional[float]] = {
        "parts_total": None,
        "grand_total": None,
        "deductible": None,
        "customer_pay": None,
        "insurance_pay": None,
    }

    for row in rows:
        row_text = _normalize_cell_text(_row_text(row))
        if not row_text:
            continue

        for label, schema_key in _MITCHELL_SUMMARY_TOTAL_LABELS.items():
            if result[schema_key] is not None:
                continue
            if label not in row_text:
                continue

            value = _parse_last_money_value(_row_text(row))
            if value is None:
                monies = _row_money_values(row)
                value = monies[-1] if monies else None
            result[schema_key] = value

    return result


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
        header_index = _find_mitchell_totals_header_row(rows)
        if header_index is not None:
            table_totals = _extract_totals_table_values(rows, header_index)
            for key, value in table_totals.items():
                if value is not None:
                    totals[key] = value

        summary_totals = _extract_summary_totals(rows)
        for key, value in summary_totals.items():
            if value is not None:
                totals[key] = value

    return totals


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


def _is_duplicate_parts_replacement(part_type: str) -> bool:
    part_type_lower = str(part_type or "").lower()
    return any(keyword in part_type_lower for keyword in _DUPLICATE_PARTS_TYPE_KEYWORDS)


def _is_non_labor_charge(description: str) -> bool:
    description_lower = str(description or "").lower()
    return any(keyword in description_lower for keyword in _NON_LABOR_DESCRIPTION_KEYWORDS)


def _normalize_parts_part_type(part_type: str) -> str:
    normalized = str(part_type or "").strip().lower()
    if "qual recycled" in normalized:
        return "LKQ"
    if "aftermarket" in normalized:
        return "A/M"
    if normalized == "new":
        return "OEM"
    return str(part_type or "").strip().upper()


def _infer_parts_part_type(
    explicit_part_type: str,
    row_text: str,
    description: str,
    operation_type: str,
    part_number: str,
) -> str:
    normalized_explicit = _normalize_parts_part_type(explicit_part_type)
    if normalized_explicit in {"OEM", "LKQ", "A/M", "SUBLET"}:
        return normalized_explicit

    combined = " ".join(
        [
            str(explicit_part_type or ""),
            str(row_text or ""),
            str(description or ""),
            str(operation_type or ""),
            str(part_number or ""),
        ]
    ).lower()

    if "qual recycled" in combined or "lkq" in combined:
        return "LKQ"
    if "aftermarket" in combined or "a/m" in combined or "a m" in combined:
        return "A/M"
    if re.search(r"\bnew\b", combined) or " oem" in f" {combined}":
        return "OEM"
    if "sublet" in combined or re.search(r"\bsubl\b", combined):
        return "SUBLET"
    return normalized_explicit


def _is_parts_replacement_from_normalized_type(normalized_part_type: str) -> bool:
    return normalized_part_type in {"OEM", "LKQ", "A/M", "SUBLET"}


def _build_parts_row_text(
    line_number: str,
    description: str,
    operation_type: str,
    total_units: Optional[float],
    part_type: str,
    part_number: str,
    qty: Optional[float],
    extended_price: Optional[float],
) -> str:
    parts = [
        str(line_number or "").strip(),
        str(description or "").strip(),
        str(operation_type or "").strip(),
        "" if total_units is None else f"{total_units:g}",
        str(part_type or "").strip(),
        str(part_number or "").strip(),
        "" if qty is None else f"{qty:g}",
        "" if extended_price is None else f"${extended_price:,.2f}",
    ]
    return " ".join(part for part in parts if part)


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

                candidate_row_text = _row_text(candidate)
                description = _extract_description(_extract_row_field(candidate, ranges, "description"))
                operation_type = _extract_row_field(candidate, ranges, "operation_type")
                total_units_raw = _extract_row_field(candidate, ranges, "total_units")
                total_units = _to_float(total_units_raw)
                part_type = _extract_row_field(candidate, ranges, "type")
                part_number = _extract_part_number(_extract_row_field(candidate, ranges, "number"))
                qty = _to_float(_extract_row_field(candidate, ranges, "qty"))
                extended_price = _to_float(_extract_row_field(candidate, ranges, "ext_price"))
                if extended_price is None or extended_price <= 0:
                    fallback_price = _parse_last_money_value(candidate_row_text)
                    if fallback_price is not None and fallback_price > 0:
                        extended_price = fallback_price
                tax_text = _extract_row_field(candidate, ranges, "tax")
                tax = str(tax_text or "").strip().lower() in {"yes", "y", "true", "tax"}

                row_key = (
                    line_number,
                    description,
                    operation_type,
                    part_type,
                    part_number,
                    str(qty if qty is not None else ""),
                    str(extended_price if extended_price is not None else ""),
                )
                if row_key in seen_rows:
                    cursor += 1
                    continue
                seen_rows.add(row_key)

                is_refinish = _is_refinish_operation(operation_type)
                is_non_labor_charge = _is_non_labor_charge(description)
                normalized_part_type = _infer_parts_part_type(
                    part_type,
                    candidate_row_text,
                    description,
                    operation_type,
                    part_number,
                )
                is_parts_replacement = _is_parts_replacement_from_normalized_type(normalized_part_type)
                is_duplicate_parts_replacement = _is_duplicate_parts_replacement(part_type)
                parts_row_text = _build_parts_row_text(
                    line_number,
                    description,
                    operation_type,
                    total_units,
                    normalized_part_type,
                    part_number,
                    qty,
                    extended_price,
                )

                if is_refinish:
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
                            "extended_price": extended_price if extended_price is not None else 0.0,
                            "total_price": extended_price if extended_price is not None else 0.0,
                            "tax": tax,
                        }
                    )

                if is_parts_replacement or is_duplicate_parts_replacement:
                    parts_items.append(
                        {
                            "line": line_number,
                            "description": description,
                            "part_type": normalized_part_type,
                            "price": extended_price if extended_price is not None else 0.0,
                            "extended_price": extended_price if extended_price is not None else 0.0,
                            "qty": qty if qty is not None else 0.0,
                            "operation_type": operation_type,
                            "total_units": total_units if total_units is not None else 0.0,
                            "number": part_number,
                            "tax": tax,
                            "row_text": parts_row_text,
                        }
                    )

                # Mitchell lines with replacement part types still carry body labor hours,
                # so keep them in labor unless they are explicitly refinish/blend operations.
                if not is_refinish and not is_non_labor_charge:
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
                            "extended_price": extended_price if extended_price is not None else 0.0,
                            "total_price": extended_price if extended_price is not None else 0.0,
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
    extracted_totals = _extract_mitchell_estimate_totals(pages)
    total_labor = sum(float(item.get("value", 0.0) or 0.0) for item in labor_items)
    total_paint = sum(float(item.get("value", 0.0) or 0.0) for item in paint_items)
    computed_parts_total = sum(float(item.get("price", 0.0) or 0.0) for item in parts_items) if parts_items else None
    parts_total = extracted_totals.get("parts_total")
    if parts_total is None:
        parts_total = computed_parts_total

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
        "grand_total": extracted_totals.get("grand_total"),
        "deductible": extracted_totals.get("deductible"),
        "customer_pay": extracted_totals.get("customer_pay"),
        "insurance_pay": extracted_totals.get("insurance_pay"),
        "body_labor": extracted_totals.get("body_labor"),
        "paint_labor": extracted_totals.get("paint_labor"),
        "frame_labor": extracted_totals.get("frame_labor"),
        "mechanical_labor": extracted_totals.get("mechanical_labor"),
        "glass_labor": extracted_totals.get("glass_labor"),
    }