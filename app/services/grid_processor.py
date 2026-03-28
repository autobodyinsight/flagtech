import re
from typing import List, Dict, Any, Tuple, Optional


def kmeans_1d(values: List[float], k: int, iters: int = 40) -> List[float]:
    """
    Simple 1D k-means clustering to find k cluster centers.
    Returns sorted list of k centers.
    """
    if not values or k <= 0:
        return []
    
    if len(values) < k:
        return sorted(set(values))
    
    # Initialize centers with evenly spaced quantiles
    sorted_vals = sorted(values)
    centers = []
    step = len(sorted_vals) / k
    for i in range(k):
        idx = int(i * step)
        if idx >= len(sorted_vals):
            idx = len(sorted_vals) - 1
        centers.append(sorted_vals[idx])
    
    # Iterate to refine centers
    for _ in range(iters):
        # Assign each value to nearest center
        clusters = [[] for _ in range(k)]
        for val in values:
            nearest_idx = min(range(k), key=lambda i: abs(val - centers[i]))
            clusters[nearest_idx].append(val)
        
        # Update centers as mean of assigned values
        new_centers = []
        for cluster in clusters:
            if cluster:
                new_centers.append(sum(cluster) / len(cluster))
            else:
                # Keep old center if cluster is empty
                new_centers.append(centers[len(new_centers)])
        
        centers = new_centers
    
    return sorted(centers)


def group_rows(words: List[Dict], y_thresh: float = 8.0) -> List[Dict]:
    """Group words into rows by y-center proximity."""
    rows = []
    for w in sorted(words, key=lambda x: (x["y0"] + x["y1"]) / 2):
        ymid = (w["y0"] + w["y1"]) / 2
        placed = False
        for r in rows:
            if abs(r["ymid"] - ymid) <= y_thresh:
                r["words"].append(w)
                r["ymid"] = sum(((ww["y0"] + ww["y1"]) / 2 for ww in r["words"])) / len(r["words"])
                placed = True
                break
        if not placed:
            rows.append({"ymid": ymid, "words": [w]})
    return rows


def _group_row_words_by_x(words: List[Dict], gap: float = 15.0) -> List[Dict]:
    """Group row words into x clusters based on spacing."""
    if not words:
        return []
    sorted_words = sorted(words, key=lambda w: w.get("x0", 0))
    groups = []
    current = [sorted_words[0]]
    for wd in sorted_words[1:]:
        prev = current[-1]
        if wd.get("x0", 0) - prev.get("x1", 0) > gap:
            groups.append(current)
            current = [wd]
        else:
            current.append(wd)
    groups.append(current)

    grouped = []
    for group in groups:
        text = " ".join(w.get("text", "") for w in group).strip()
        grouped.append({
            "words": group,
            "text": text,
            "min_x": min(w.get("x0", 0) for w in group),
            "max_x": max(w.get("x1", 0) for w in group),
        })
    return grouped


def detect_anchors_and_vehicle_info(
    pages: List[Dict]
) -> Tuple[Optional[int], Optional[float], Optional[int], Optional[float], str, str, str, str, str, str]:
    """
    Detect anchor points in PDF and extract vehicle information, owner info, insurance company, and VIN.
    Returns:
        (anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, insurance_company, vin, claim_number)
    """
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    first_ro_line = ""
    vehicle_info_line = ""
    owner_info = ""
    insurance_company = ""
    vin = ""
    claim_number = ""
    vin_row_idx = None
    ro_anchor_page = None
    ro_anchor_ymid = None
    customer_anchor_page = None
    customer_anchor_ymid = None
    owner_anchor_page = None
    owner_anchor_ymid = None

    def _is_ro_number_row(text: str) -> bool:
        return bool(
            re.search(r"\bRO\b\s*(NUMBER|NO\.?)\b", text, re.IGNORECASE)
            or re.search(r"\bRO\s*#", text, re.IGNORECASE)
        )

    def _is_customer_row(text: str) -> bool:
        return bool(re.search(r"\bCUSTOMER\s*:", text, re.IGNORECASE))

    def _is_owner_row(text: str) -> bool:
        return bool(re.search(r"\bOWNER\s*:", text, re.IGNORECASE))

    def _is_vin_or_vehicle_row(text: str) -> bool:
        return bool(re.search(r"\b(VIN|VEHICLE)\b", text, re.IGNORECASE))

    def _extract_claim_number_from_text(text: str) -> str:
        match = re.search(
            r"\bCLAIM\b\s*(?:NUMBER|NO\.?|#)?\s*[:#]?\s*([A-Za-z0-9-]{4,})",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)
        compact = re.sub(r"\s+", "", text)
        match = re.search(
            r"CLAIM(?:NUMBER|NO|#)?[:#]?([A-Za-z0-9-]{4,})",
            compact,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)
        return ""

    header_started = False
    header_ended = False

    for pi, page in enumerate(pages, start=1):
        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for idx, r in enumerate(rows):
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()

            if not header_started and _is_ro_number_row(row_text):
                header_started = True

            if header_started and not header_ended and _is_vin_or_vehicle_row(row_text):
                header_ended = True

            if header_started and not header_ended and not claim_number:
                if re.search(r"\bCLAIM\b", row_text, re.IGNORECASE):
                    claim_number = _extract_claim_number_from_text(row_text)

            # Anchor priority: RO Number -> Customer: -> Owner
            if _is_ro_number_row(row_text):
                ro_count += 1
                if ro_count == 1 and not first_ro_line:
                    first_ro_line = row_text
                if ro_anchor_page is None:
                    ro_anchor_page = pi
                    ro_anchor_ymid = r["ymid"]

            if customer_anchor_page is None and _is_customer_row(row_text):
                customer_anchor_page = pi
                customer_anchor_ymid = r["ymid"]

            if owner_anchor_page is None and _is_owner_row(row_text):
                owner_anchor_page = pi
                owner_anchor_ymid = r["ymid"]

            # Extract owner info (look for "owner:" or "customer:" and extract name/phone in the same x column)
            if re.search(r"\b(owner|customer)\s*:", row_text, re.IGNORECASE):
                name = ""
                phone = ""

                header_groups = _group_row_words_by_x(r["words"])
                owner_group = None
                for group in header_groups:
                    if re.search(r"\b(owner|customer)\b", group["text"], re.IGNORECASE):
                        owner_group = group
                        break

                left_bound = None
                right_bound = None
                if owner_group:
                    left_bound = owner_group["min_x"] - 2
                    for group in header_groups:
                        if group["min_x"] > owner_group["max_x"]:
                            right_bound = group["min_x"] - 2
                            break

                def _row_text_in_bounds(row: Dict) -> str:
                    words = row.get("words", [])
                    if left_bound is None:
                        filtered_words = words
                    else:
                        filtered_words = [
                            w for w in words
                            if w.get("xmid", 0) >= left_bound and (right_bound is None or w.get("xmid", 0) < right_bound)
                        ]
                    return " ".join(
                        w.get("text", "") for w in sorted(filtered_words, key=lambda w: w.get("x0", 0))
                    ).strip()

                # Scan the next rows for name and phone within the same x column.
                scan_end = min(len(rows), idx + 10)
                for j in range(idx + 1, scan_end):
                    full_line = _row_text_in_bounds(rows[j])
                    if not full_line:
                        continue
                    name_match = re.match(r"^([A-Za-z][A-Za-z\-\s']*,\s*[A-Za-z][A-Za-z\-\s']*)", full_line)
                    if name_match:
                        name = name_match.group(1)
                        break

                for j in range(idx + 1, scan_end):
                    full_line = _row_text_in_bounds(rows[j])
                    if not full_line:
                        continue
                    phone_match = re.search(
                        r"(\(\d{3}\)\s*\d{3}-\d{4})\s*(cell|work|home|mobile)?",
                        full_line,
                        re.IGNORECASE,
                    )
                    if phone_match:
                        phone = phone_match.group(1).strip()
                        if phone_match.group(2):
                            phone += " " + phone_match.group(2).strip()
                        break

                # Only store name and phone
                if name or phone:
                    owner_info_parts = []
                    if name:
                        owner_info_parts.append(name)
                    if phone:
                        owner_info_parts.append(phone)
                    owner_info = "\n".join(owner_info_parts)

            # Extract insurance company (look for "insurance:" or "insurance company:" and take next line)
            if re.search(r"\binsurance(?:\s+company)?\s*:", row_text, re.IGNORECASE):
                if idx + 1 < len(rows):
                    header_groups = _group_row_words_by_x(r["words"])
                    insurance_group = None
                    for group in header_groups:
                        lower_text = group["text"].lower()
                        if "insurance" in lower_text:
                            insurance_group = group
                            break

                    next_row_words = rows[idx + 1]["words"]
                    filtered_words = next_row_words
                    if insurance_group:
                        left_bound = insurance_group["min_x"] - 2
                        right_bound = None
                        for group in header_groups:
                            if group["min_x"] > insurance_group["max_x"]:
                                right_bound = group["min_x"] - 2
                                break
                        filtered_words = [
                            w for w in next_row_words
                            if w.get("xmid", 0) >= left_bound and (right_bound is None or w.get("xmid", 0) < right_bound)
                        ]

                    raw_company = " ".join(w.get("text", "") for w in sorted(filtered_words, key=lambda w: w.get("x0", 0))).strip()
                    cleaned_company = raw_company
                    # Drop leading owner name if it appears at the start of the line.
                    cleaned_company = re.sub(r"^[A-Za-z][A-Za-z\-]*,\s*[A-Za-z][A-Za-z\-]*\s+", "", cleaned_company)
                    insurance_company = cleaned_company

            # Extract VIN (look for "VIN:" and capture the 17-character value)
            if re.search(r"\bVIN\b", row_text, re.IGNORECASE):
                vin_row_idx = idx
                
                # Capture the first line above VIN that contains a valid year (1900-2070)
                if idx > 0:
                    year_pattern = re.compile(r"\b(19\d{2}|20[0-6]\d|2070)\b")
                    for j in range(idx - 1, -1, -1):
                        text = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        if not text:
                            continue
                        if year_pattern.search(text):
                            vehicle_info_line = text
                            break
                
                # Look for 17-character alphanumeric value after VIN
                vin_match = re.search(r"VIN\s*[:#-]*\s*([A-Za-z0-9]{17})", row_text, re.IGNORECASE)
                if vin_match:
                    vin = vin_match.group(1)
                else:
                    # Try next line if not on same line
                    for j in range(idx + 1, min(idx + 2, len(rows))):
                        next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        vin_match = re.search(r"([A-Za-z0-9]{17})", next_line)
                        if vin_match:
                            vin = vin_match.group(1)
                            break

            if not subtotals_page:
                if re.search(r"\bESTIMATE\s+TOTALS\b", row_text, re.IGNORECASE):
                    subtotals_page = pi
                    subtotals_ymid = r["ymid"]
                else:
                    upper = row_text.upper()
                    if "ESTIMATE" in upper and idx + 1 < len(rows):
                        next_text = " ".join(w.get("text", "") for w in rows[idx + 1]["words"]).strip()
                        if re.search(r"\bTOTALS\b", next_text, re.IGNORECASE):
                            subtotals_page = pi
                            subtotals_ymid = rows[idx + 1]["ymid"]

        if ro_anchor_page and subtotals_page:
            break

    if ro_anchor_page is not None:
        anchor_page = ro_anchor_page
        anchor_ymid = ro_anchor_ymid
    elif customer_anchor_page is not None:
        anchor_page = customer_anchor_page
        anchor_ymid = customer_anchor_ymid
    elif owner_anchor_page is not None:
        anchor_page = owner_anchor_page
        anchor_ymid = owner_anchor_ymid

    return anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, insurance_company, vin, claim_number


def collect_words_in_range(
    pages: List[Dict],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
) -> List[Dict]:
    """Collect all words within the anchor and subtotals vertical range."""
    all_words = []
    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) > subtotals_ymid:
                    continue
            all_words.append(wd)

    return all_words


def detect_header_columns(
    pages: List[Dict],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
) -> Dict[str, Optional[float]]:
    """
    Detect column x-positions by finding the header row containing:
    LINE, OPER, DESCRIPTION, PART, QTY, EXTENDED, LABOR, PAINT.
    """
    header_columns = {
        "line": None,
        "oper": None,
        "description": None,
        "part_number": None,
        "qty": None,
        "ext_price": None,
        "labor": None,
        "paint": None,
    }

    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        page_words = []
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)

        rows = group_rows(page_words, y_thresh=6.0)

        for row in rows:
            row_text_upper = " ".join(w["text"] for w in row["words"]).upper()

            if all(token in row_text_upper for token in ["LINE", "OPER", "DESCRIPTION", "LABOR", "PAINT"]):
                for wd in row["words"]:
                    txt = wd["text"].upper()
                    xmid = wd["xmid"]

                    if "LINE" in txt and header_columns["line"] is None:
                        header_columns["line"] = xmid
                    elif "OPER" in txt and header_columns["oper"] is None:
                        header_columns["oper"] = xmid
                    elif "DESC" in txt or "DESCRIPTION" in txt:
                        header_columns["description"] = xmid
                    elif "PART" in txt and header_columns["part_number"] is None:
                        header_columns["part_number"] = xmid
                    elif "QTY" in txt and header_columns["qty"] is None:
                        header_columns["qty"] = xmid
                    elif ("EXT" in txt or "EXTENDED" in txt) and header_columns["ext_price"] is None:
                        header_columns["ext_price"] = xmid
                    elif "LABOR" in txt and header_columns["labor"] is None:
                        header_columns["labor"] = xmid
                    elif "PAINT" in txt and header_columns["paint"] is None:
                        header_columns["paint"] = xmid

                return header_columns

    return header_columns


def _parse_numeric_or_incl(text: str) -> Optional[float]:
    """Parse numeric or 'Incl'. Returns float or None."""
    t = text.strip()
    if not t:
        return None
    if t.lower() == "incl":
        return 0.0
    if re.match(r'^-?\d+(?:\.\d+)?$', t):
        try:
            return float(t)
        except Exception:
            return None
    return None


def extract_labor_paint_items(
    pages: List[Dict],
    columns: Dict[str, Optional[float]],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract labor and paint items using CCC rules.
    """
    labor_items = []
    paint_items = []

    col_tol = 25.0

    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        page_words = []
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd["ymid"] < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd["ymid"] >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)

        rows = group_rows(page_words, y_thresh=6.0)

        for row in rows:
            row_words = sorted(row["words"], key=lambda x: x["xmid"])

            line_num = None
            labor_val = None
            paint_val = None
            description_parts = []

            for wd in row_words:
                word_xmid = wd["xmid"]
                word_text = wd["text"].strip()

                # Line number
                if columns["line"] is not None and abs(word_xmid - columns["line"]) < col_tol:
                    if re.match(r'^\d{1,3}$', word_text):
                        line_num = word_text

                # Description from LINE to QTY to capture full text
                if columns["line"] is not None and columns["qty"] is not None:
                    if columns["line"] + col_tol < word_xmid < columns["qty"] - col_tol:
                        description_parts.append(word_text)

                # Labor
                if columns["labor"] is not None and abs(word_xmid - columns["labor"]) < col_tol:
                    parsed = _parse_numeric_or_incl(word_text)
                    if parsed is not None and parsed != 0.0 and -99.9 <= parsed <= 99.9:
                        labor_val = parsed

                # Paint
                if columns["paint"] is not None and abs(word_xmid - columns["paint"]) < col_tol:
                    parsed = _parse_numeric_or_incl(word_text)
                    if parsed is not None and parsed != 0.0 and -99.9 <= parsed <= 99.9:
                        paint_val = parsed

            desc_text = " ".join(description_parts).strip()
            desc_lower = desc_text.lower()

            # Clear coat lines are paint-only, exclude from labor
            is_clear_coat = "add for clear coat" in desc_lower

            # Labor override for REPL or R&I
            is_repl_or_ri = ("repl" in desc_lower) or ("r&i" in desc_lower)

            if line_num and (labor_val is not None or is_repl_or_ri) and not is_clear_coat:
                labor_items.append({
                    "line": line_num,
                    "description": desc_text,
                    "value": labor_val if labor_val is not None else 0.0,
                })

            if line_num and paint_val is not None:
                paint_items.append({
                    "line": line_num,
                    "description": desc_text,
                    "value": paint_val,
                })

    return labor_items, paint_items


def _parse_int(text: str) -> Optional[int]:
    t = text.strip().replace(",", "")
    if not t:
        return None
    # Extract leading digits from the text (handles cases like "4 **" or "4 <>")
    match = re.match(r"^(\d+)", t)
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


def _parse_float(text: str) -> Optional[float]:
    t = text.strip().replace(",", "")
    if not t:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", t)
    if not match:
        return None
    try:
        return float(match.group(0))
    except Exception:
        return None


def _parse_part_type(text: str) -> str:
    t = text.upper()
    if "LKQ" in t:
        return "LKQ"
    if "A/M" in t or "A M" in t or "AFTERMARKET" in t:
        return "A/M"
    if "OEM" in t:
        return "OEM"
    return ""


def extract_parts_items(
    pages: List[Dict],
    columns: Dict[str, Optional[float]],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
) -> List[Dict]:
    """Extract parts lines using detected columns."""
    parts_items: List[Dict] = []
    col_tol = 25.0

    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        page_words = []
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd["ymid"] < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd["ymid"] >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)

        rows = group_rows(page_words, y_thresh=6.0)

        for row in rows:
            row_words = sorted(row["words"], key=lambda x: x["xmid"])
            row_text = " ".join(w.get("text", "") for w in row_words).strip()
            row_text_upper = row_text.upper()

            if all(token in row_text_upper for token in ["LINE", "OPER", "DESCRIPTION"]):
                continue

            line_text = ""
            qty_text = ""
            ext_text = ""
            description_parts = []

            for w in row_words:
                if columns.get("line") is not None and abs(w["xmid"] - columns["line"]) <= col_tol:
                    line_text += (w["text"] + " ")
                    continue
                if columns.get("qty") is not None and abs(w["xmid"] - columns["qty"]) <= col_tol:
                    qty_text += (w["text"] + " ")
                    continue
                if columns.get("ext_price") is not None and abs(w["xmid"] - columns["ext_price"]) <= col_tol:
                    ext_text += (w["text"] + " ")
                    continue

                left_bound = columns.get("line")
                right_bound = columns.get("ext_price") or columns.get("qty")
                if left_bound is not None and right_bound is not None:
                    if left_bound + col_tol < w["xmid"] < right_bound - col_tol:
                        description_parts.append(w["text"])

            line_text = line_text.strip()
            qty_text = qty_text.strip()
            ext_text = ext_text.strip()
            desc_text = " ".join(description_parts).strip()

            qty_val = _parse_float(qty_text) if qty_text else None
            if qty_val is None or qty_val < 1:
                continue

            line_num = _parse_int(line_text) if line_text else None
            price_val = _parse_float(ext_text) if ext_text else None

            part_type = _parse_part_type(desc_text)

            parts_items.append({
                "line": line_num,
                "description": desc_text,
                "part_type": part_type,
                "price": price_val if price_val is not None else 0.0,
                "qty": qty_val,
                "row_text": row_text,
            })

    return parts_items





def process_pdf_grid(pages: List[Dict]) -> Dict[str, Any]:
    """Main entry point."""
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            w["ymid"] = (w["y0"] + w["y1"]) / 2.0

    anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, insurance_company, vin, claim_number = \
        detect_anchors_and_vehicle_info(pages)

    all_words = collect_words_in_range(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    columns = detect_header_columns(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    labor_items, paint_items = extract_labor_paint_items(
        pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid
    )

    parts_items = extract_parts_items(
        pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid
    )

    full_text_lines: List[str] = []
    for page in pages:
        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for row in rows:
            row_text = " ".join(
                word.get("text", "") for word in sorted(row.get("words", []), key=lambda item: item.get("x0", 0))
            ).strip()
            if row_text:
                full_text_lines.append(row_text)

    def _extract_line_value(lines: List[str], pattern: str) -> str:
        for line in lines:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return (match.group(1) or "").strip()
        return ""

    def _sanitize_name_only(value: str) -> str:
        base = str(value or "").split(",", 1)[0]
        alpha_only = re.sub(r"[^A-Za-z\s]", "", base)
        return re.sub(r"\s+", " ", alpha_only).strip()

    written_by = ""
    estimator = ""
    if not written_by:
        written_by = _sanitize_name_only(_extract_line_value(full_text_lines, r"\bwritten\s+by\b\s*:\s*(.*)$"))
    if not estimator:
        estimator = _sanitize_name_only(_extract_line_value(full_text_lines, r"\bestimator\b\s*:\s*(.*)$"))

    total_labor = sum(item["value"] for item in labor_items)
    total_paint = sum(item["value"] for item in paint_items)

    totals = {
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

    def _extract_last_numeric(text: str) -> Optional[float | str]:
        matches = re.findall(r"[\d,.]+", text)
        if not matches:
            return None
        raw = matches[-1]
        numeric = raw.replace(",", "")
        try:
            return float(numeric)
        except Exception:
            return raw

    def _extract_rightmost_numeric(row: Dict) -> Optional[float | str]:
        candidates = []
        for word in row.get("words", []):
            text = str(word.get("text", "")).strip()
            if not text or not re.search(r"\d", text):
                continue
            cleaned = re.sub(r"[^0-9.\-]", "", text)
            if not cleaned or cleaned in {"-", "."}:
                continue
            candidates.append((word.get("x0", 0), cleaned))

        if not candidates:
            return None

        _, raw = max(candidates, key=lambda item: item[0])
        try:
            return float(raw.replace(",", ""))
        except Exception:
            return raw

    def _apply_totals_from_row(text: str, row: Dict, next_upper: str, prev_upper: str) -> None:
        upper = text.upper()
        rightmost_value = _extract_rightmost_numeric(row)

        def _matches_any(patterns: List[str]) -> bool:
            return any(re.search(pattern, upper) for pattern in patterns)

        parts_row = (
            re.search(r"\bPARTS TOTAL\b", upper)
            or ("PARTS" in upper and "TOTAL" in upper)
            or ("PARTS" in upper and "TOTAL" in next_upper)
            or ("TOTAL" in upper and "PARTS" in prev_upper)
            or re.search(r"\bPARTS\b", upper)
        )
        if totals["parts_total"] is None and parts_row:
            totals["parts_total"] = rightmost_value or _extract_last_numeric(text)
        if totals["grand_total"] is None and re.search(r"\bGRAND TOTAL\b", upper):
            totals["grand_total"] = rightmost_value or _extract_last_numeric(text)
        if totals["deductible"] is None and re.search(r"\bDEDUCTIBLE\b", upper):
            totals["deductible"] = rightmost_value or _extract_last_numeric(text)
        if totals["customer_pay"] is None and (
            re.search(r"\bCUSTOMER\s+PAY\b", upper)
            or re.search(r"\bCUSTOMER\b.*\bPAY\b", upper)
            or re.search(r"\bCUSTOMER\s+TOTAL\b", upper)
        ):
            totals["customer_pay"] = rightmost_value or _extract_last_numeric(text)
        if totals["insurance_pay"] is None and (
            re.search(r"\bINSURANCE\s+PAY\b", upper)
            or re.search(r"\bINSURANCE\b.*\bPAY\b", upper)
            or re.search(r"\bINSURANCE\s+TOTAL\b", upper)
        ):
            totals["insurance_pay"] = rightmost_value or _extract_last_numeric(text)

        if totals["body_labor"] is None and _matches_any([
            r"\bBODY\s+LABOR\b",
            r"\bLABOR\s*,?\s*BODY\b",
        ]):
            totals["body_labor"] = rightmost_value or _extract_last_numeric(text)

        if totals["paint_labor"] is None and _matches_any([
            r"\bPAINT\s+LABOR\b",
            r"\bLABOR\s*,?\s*REFINISH\b",
        ]):
            totals["paint_labor"] = rightmost_value or _extract_last_numeric(text)

        if totals["frame_labor"] is None and _matches_any([
            r"\bFRAME\s+LABOR\b",
            r"\bLABOR\s*,?\s*FRAME\b",
        ]):
            totals["frame_labor"] = rightmost_value or _extract_last_numeric(text)

        if totals["mechanical_labor"] is None and _matches_any([
            r"\bMECHANICAL\s+LABOR\b",
            r"\bLABOR\s*,?\s*MECHANICAL\b",
        ]):
            totals["mechanical_labor"] = rightmost_value or _extract_last_numeric(text)

        if totals["glass_labor"] is None and _matches_any([
            r"\bGLASS\s+LABOR\b",
            r"\bLABOR\s*,?\s*GLASS\b",
        ]):
            totals["glass_labor"] = rightmost_value or _extract_last_numeric(text)

    if subtotals_page:
        for pi, page in enumerate(pages, start=1):
            if pi < subtotals_page:
                continue
            rows = group_rows(page.get("words", []), y_thresh=6.0)
            for idx, r in enumerate(rows):
                row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
                if re.search(r"\bESTIMATE\s+TOTALS\b", row_text, re.IGNORECASE):
                    scan_end = min(len(rows), idx + 16)
                    for follow_idx in range(idx + 1, scan_end):
                        follow_row = rows[follow_idx]
                        follow_text = " ".join(w.get("text", "") for w in follow_row["words"]).strip()
                        next_upper = ""
                        if follow_idx + 1 < len(rows):
                            next_text = " ".join(w.get("text", "") for w in rows[follow_idx + 1]["words"]).strip()
                            next_upper = next_text.upper()
                        prev_upper = ""
                        if follow_idx - 1 >= 0:
                            prev_text = " ".join(w.get("text", "") for w in rows[follow_idx - 1]["words"]).strip()
                            prev_upper = prev_text.upper()
                        _apply_totals_from_row(follow_text, follow_row, next_upper, prev_upper)
                    break
            if any(value is not None for value in totals.values()):
                break

    if not any(value is not None for value in totals.values()):
        for page in pages:
            rows = group_rows(page.get("words", []), y_thresh=6.0)
            for idx, r in enumerate(rows):
                text = " ".join(w.get("text", "") for w in r["words"]).strip()
                next_upper = ""
                if idx + 1 < len(rows):
                    next_text = " ".join(w.get("text", "") for w in rows[idx + 1]["words"]).strip()
                    next_upper = next_text.upper()
                prev_upper = ""
                if idx - 1 >= 0:
                    prev_text = " ".join(w.get("text", "") for w in rows[idx - 1]["words"]).strip()
                    prev_upper = prev_text.upper()
                _apply_totals_from_row(text, r, next_upper, prev_upper)
            if any(value is not None for value in totals.values()):
                break

    def _to_float(value: Optional[float | str]) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = re.sub(r"[^0-9.\-]", "", str(value))
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except Exception:
            return None

    if totals["customer_pay"] is None and totals["deductible"] is not None:
        totals["customer_pay"] = totals["deductible"]

    if totals["customer_pay"] is None and totals["deductible"] is None:
        grand_total_val = _to_float(totals["grand_total"])
        insurance_pay_val = _to_float(totals["insurance_pay"])
        if grand_total_val is not None and insurance_pay_val is not None:
            totals["customer_pay"] = round(grand_total_val - insurance_pay_val, 2)

    return {
        "labor_items": labor_items,
        "paint_items": paint_items,
        "parts_items": parts_items,
        "total_labor": total_labor,
        "total_paint": total_paint,
        "first_ro_line": first_ro_line,
        "second_ro_line": first_ro_line,  # Keep for backward compatibility
        "vehicle_info_line": vehicle_info_line,
        "owner_info": owner_info,
        "insurance_company": insurance_company,
        "written_by": written_by,
        "estimator": estimator,
        "vin": vin,
        "claim_number": claim_number,
        "anchor_page": anchor_page,
        "anchor_ymid": anchor_ymid,
        "subtotals_page": subtotals_page,
        "subtotals_ymid": subtotals_ymid,
        "parts_total": totals["parts_total"],
        "grand_total": totals["grand_total"],
        "deductible": totals["deductible"],
        "customer_pay": totals["customer_pay"],
        "insurance_pay": totals["insurance_pay"],
        "body_labor": totals["body_labor"],
        "paint_labor": totals["paint_labor"],
        "frame_labor": totals["frame_labor"],
        "mechanical_labor": totals["mechanical_labor"],
        "glass_labor": totals["glass_labor"],
    }


def generate_pages_html(
    pages: List[Dict],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
    display_w: int = 1200,
) -> str:
    """Generate HTML visualization."""
    pages_html = ""

    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        w = page.get("width", 1)
        h = page.get("height", 1)
        scale = display_w / w if w else 1.0

        boxes_html = ""
        page_words = []

        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd["ymid"] < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd["ymid"] >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)

        for wd in page_words:
            x = wd["x0"] * scale
            y = wd["y0"] * scale
            ww = (wd["x1"] - wd["x0"]) * scale
            hh = (wd["y1"] - wd["y0"]) * scale
            txt = wd["text"].replace("<", "&lt;").replace(">", "&gt;")
            boxes_html += (
                f"<div style='position:absolute; left:{x}px; top:{y}px; "
                f"width:{ww}px; height:{hh}px; font-size:15px; overflow:hidden;'>{txt}</div>"
            )

        pages_html += (
            f"<h3>Page {pi}</h3>"
            f"<div style='position:relative; width:{display_w}px; height:{int(h*scale)}px; "
            f"border:1px solid #ccc; margin-bottom:20px;'>{boxes_html}</div>"
        )

    return pages_html