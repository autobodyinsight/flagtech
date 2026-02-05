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


def detect_anchors_and_vehicle_info(
    pages: List[Dict]
) -> Tuple[Optional[int], Optional[float], Optional[int], Optional[float], str, str, str, str, str]:
    """
    Detect anchor points in PDF and extract vehicle information, owner info, and VIN.
    Returns:
        (anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, vin)
    """
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    first_ro_line = ""
    vehicle_info_line = ""
    owner_info = ""
    vin = ""

    for pi, page in enumerate(pages, start=1):
        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for idx, r in enumerate(rows):
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()

            # Extract first RO
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 1 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
                    first_ro_line = row_text

                    # Look for vehicle info in next lines
                    for j in range(idx + 1, min(idx + 10, len(rows))):
                        next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        if re.search(r'\b(19\d{2}|20\d{2})\b', next_line):
                            vehicle_info_line = next_line
                            break

            # Extract owner info (look for "owner:" and capture next line)
            if re.search(r"\bowner\b", row_text, re.IGNORECASE):
                for j in range(idx + 1, min(idx + 3, len(rows))):
                    next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                    # Try to match phone pattern (000) 000-0000 or similar
                    if re.search(r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}', next_line) or next_line:
                        owner_info = next_line
                        break

            # Extract VIN (look for "VIN:" and capture the 17-character value)
            if re.search(r"\bVIN\b", row_text, re.IGNORECASE):
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

            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]

        if anchor_page and subtotals_page:
            break

    return anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, vin


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
    if re.match(r"^\d+$", t):
        try:
            return int(t)
        except Exception:
            return None
    return None


def _parse_float(text: str) -> Optional[float]:
    t = text.strip().replace(",", "")
    if not t:
        return None
    if re.match(r"^-?\d+(?:\.\d+)?$", t):
        try:
            return float(t)
        except Exception:
            return None
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
            desc_text = ""
            part_text = ""
            qty_text = ""
            ext_text = ""

            for w in row_words:
                if columns.get("line") is not None and abs(w["xmid"] - columns["line"]) <= col_tol:
                    line_text += (w["text"] + " ")
                    continue
                if columns.get("part_number") is not None and abs(w["xmid"] - columns["part_number"]) <= col_tol:
                    part_text += (w["text"] + " ")
                    continue
                if columns.get("qty") is not None and abs(w["xmid"] - columns["qty"]) <= col_tol:
                    qty_text += (w["text"] + " ")
                    continue
                if columns.get("ext_price") is not None and abs(w["xmid"] - columns["ext_price"]) <= col_tol:
                    ext_text += (w["text"] + " ")
                    continue
                if columns.get("description") is not None and abs(w["xmid"] - columns["description"]) <= col_tol:
                    desc_text += (w["text"] + " ")

            line_text = line_text.strip()
            desc_text = desc_text.strip()
            part_text = part_text.strip()
            qty_text = qty_text.strip()
            ext_text = ext_text.strip()

            if not part_text and not qty_text and not ext_text:
                continue

            line_num = _parse_int(line_text) if line_text else None
            qty_val = _parse_float(qty_text) if qty_text else None
            price_val = _parse_float(ext_text) if ext_text else None

            part_type = _parse_part_type(" ".join([desc_text, part_text]))

            parts_items.append({
                "line": line_num,
                "description": desc_text or part_text,
                "part_type": part_type,
                "price": price_val if price_val is not None else 0.0,
                "qty": qty_val if qty_val is not None else 1,
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

    anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, first_ro_line, vehicle_info_line, owner_info, vin = \
        detect_anchors_and_vehicle_info(pages)

    all_words = collect_words_in_range(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    columns = detect_header_columns(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    labor_items, paint_items = extract_labor_paint_items(
        pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid
    )

    parts_items = extract_parts_items(
        pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid
    )

    total_labor = sum(item["value"] for item in labor_items)
    total_paint = sum(item["value"] for item in paint_items)

    totals = {
        "parts_total": None,
        "grand_total": None,
        "deductible": None,
        "customer_pay": None,
        "insurance_pay": None,
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
                        upper = follow_text.upper()
                        rightmost_value = _extract_rightmost_numeric(follow_row)

                        next_upper = ""
                        if follow_idx + 1 < len(rows):
                            next_text = " ".join(w.get("text", "") for w in rows[follow_idx + 1]["words"]).strip()
                            next_upper = next_text.upper()
                        prev_upper = ""
                        if follow_idx - 1 >= 0:
                            prev_text = " ".join(w.get("text", "") for w in rows[follow_idx - 1]["words"]).strip()
                            prev_upper = prev_text.upper()

                        parts_row = (
                            re.search(r"\bPARTS TOTAL\b", upper)
                            or ("PARTS" in upper and "TOTAL" in upper)
                            or ("PARTS" in upper and "TOTAL" in next_upper)
                            or ("TOTAL" in upper and "PARTS" in prev_upper)
                            or re.search(r"\bPARTS\b", upper)
                        )
                        if totals["parts_total"] is None and parts_row:
                            totals["parts_total"] = rightmost_value or _extract_last_numeric(follow_text)
                        if totals["grand_total"] is None and re.search(r"\bGRAND TOTAL\b", upper):
                            totals["grand_total"] = rightmost_value or _extract_last_numeric(follow_text)
                        if totals["deductible"] is None and re.search(r"\bDEDUCTIBLE\b", upper):
                            totals["deductible"] = rightmost_value or _extract_last_numeric(follow_text)
                        if totals["customer_pay"] is None and (
                            re.search(r"\bCUSTOMER PAY\b", upper) or re.search(r"\bCUSTOMER\b.*\bPAY\b", upper)
                        ):
                            totals["customer_pay"] = rightmost_value or _extract_last_numeric(follow_text)
                        if totals["insurance_pay"] is None and (
                            re.search(r"\bINSURANCE PAY\b", upper) or re.search(r"\bINSURANCE\b.*\bPAY\b", upper)
                        ):
                            totals["insurance_pay"] = rightmost_value or _extract_last_numeric(follow_text)
                    break
            if any(value is not None for value in totals.values()):
                break

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
        "vin": vin,
        "anchor_page": anchor_page,
        "anchor_ymid": anchor_ymid,
        "subtotals_page": subtotals_page,
        "subtotals_ymid": subtotals_ymid,
        "parts_total": totals["parts_total"],
        "grand_total": totals["grand_total"],
        "deductible": totals["deductible"],
        "customer_pay": totals["customer_pay"],
        "insurance_pay": totals["insurance_pay"],
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