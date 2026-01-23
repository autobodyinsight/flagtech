import re
from typing import List, Dict, Any, Tuple, Optional


def group_rows(words: List[Dict], y_thresh: float = 8.0) -> List[Dict]:
    """Group words into rows by y-center proximity."""
    rows = []
    for w in sorted(words, key=lambda x: (x["y0"] + x["y1"]) / 2):
        ymid = (w["y0"] + w["y1"]) / 2
        placed = False
        for r in rows:
            if abs(r["ymid"] - ymid) <= y_thresh:
                r["words"].append(w)
                # Update average ymid
                r["ymid"] = sum(((ww["y0"] + ww["y1"]) / 2 for ww in r["words"])) / len(r["words"])
                placed = True
                break
        if not placed:
            rows.append({"ymid": ymid, "words": [w]})
    return rows


def detect_anchors_and_vehicle_info(
    pages: List[Dict]
) -> Tuple[Optional[int], Optional[float], Optional[int], Optional[float], str, str]:
    """
    Detect anchor points in PDF and extract vehicle information.

    Returns:
        (anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, second_ro_line, vehicle_info_line)
    """
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    second_ro_line = ""
    vehicle_info_line = ""

    for pi, page in enumerate(pages, start=1):
        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for idx, r in enumerate(rows):
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()

            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
                    second_ro_line = row_text

                    # Search for vehicle info line (contains 4-digit year)
                    for j in range(idx + 1, min(idx + 10, len(rows))):
                        next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        if re.search(r'\b(19\d{2}|20\d{2})\b', next_line):
                            vehicle_info_line = next_line
                            break

            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]

        if anchor_page and subtotals_page:
            break

    return anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, second_ro_line, vehicle_info_line


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
    LINE, OPER, DESCRIPTION, PART, QTY, EXTENDED (or EXT), LABOR, PAINT.
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

        # Filter words in range for this page
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

            # Require key headers to be present
            if all(
                token in row_text_upper
                for token in ["LINE", "OPER", "DESCRIPTION", "LABOR", "PAINT"]
            ):
                # Map each header word to a column by its text
                for wd in row["words"]:
                    txt = wd["text"].upper()
                    xmid = wd.get("xmid", (wd["x0"] + wd["x1"]) / 2.0)

                    if "LINE" in txt and header_columns["line"] is None:
                        header_columns["line"] = xmid
                    elif "OPER" in txt and header_columns["oper"] is None:
                        header_columns["oper"] = xmid
                    elif "DESC" in txt or "DESCRIPTION" in txt:
                        if header_columns["description"] is None:
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

                # Once we find a header row, we can stop
                return header_columns

    return header_columns


def _parse_numeric_or_incl(text: str) -> Optional[float]:
    """
    Parse a numeric value or 'Incl' into a float.
    Returns:
        float value, or 0.0 for 'Incl', or None if invalid.
    """
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
    Extract labor and paint items from pages using the detected header columns.

    Rules (CCC-specific):
    - A repair line is valid if it has a line number in the Line column.
    - A labor line is valid if:
        - It has a line number, AND
        - Labor column has a value in [-99.9, 99.9] or 'Incl',
        - BUT NOT 0.0 (0.0 means not a labor line).
    - A paint line is valid if:
        - It has a line number, AND
        - Paint column has a value in [-99.9, 99.9] or 'Incl',
        - BUT NOT 0.0 (0.0 means not a paint line).
    - Multi-line descriptions are allowed, but only the first line has the line number.
      We do not need to merge; we treat each row independently.
    """
    labor_items: List[Dict] = []
    paint_items: List[Dict] = []

    line_col_x = columns.get("line")
    labor_col_x = columns.get("labor")
    paint_col_x = columns.get("paint")
    desc_col_x = columns.get("description")

    # Reasonable horizontal tolerance around each column
    col_tol = 25.0

    for pi, page in enumerate(pages, start=1):
        # Skip pages outside range
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue

        # Filter words in range for this page
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
            row_words = sorted(row["words"], key=lambda x: x.get("xmid", (x["x0"] + x["x1"]) / 2.0))
            row_ymid = row["ymid"]

            line_num: Optional[str] = None
            labor_val: Optional[float] = None
            paint_val: Optional[float] = None
            description_parts: List[str] = []

            for wd in row_words:
                word_xmid = wd.get("xmid", (wd["x0"] + wd["x1"]) / 2.0)
                word_text = wd["text"].strip()

                # Line column: detect line number (1-3 digits)
                if line_col_x is not None and abs(word_xmid - line_col_x) < col_tol:
                    if re.match(r'^\d{1,3}$', word_text):
                        line_num = word_text

                # Description: any text between OPER and QTY columns
                if columns["oper"] is not None and columns["qty"] is not None:
                    if columns["oper"] + col_tol < word_xmid < columns["qty"] - col_tol:
                        description_parts.append(word_text)

                # Labor column
                if labor_col_x is not None and abs(word_xmid - labor_col_x) < col_tol:
                    parsed = _parse_numeric_or_incl(word_text)
                    if parsed is not None:
                        # Valid numeric or 'Incl'
                        # But 0.0 means NOT a labor line
                        if parsed != 0.0 and -99.9 <= parsed <= 99.9:
                            labor_val = parsed

                # Paint column
                if paint_col_x is not None and abs(word_xmid - paint_col_x) < col_tol:
                    parsed = _parse_numeric_or_incl(word_text)
                    if parsed is not None:
                        # Valid numeric or 'Incl'
                        # But 0.0 means NOT a paint line
                        if parsed != 0.0 and -99.9 <= parsed <= 99.9:
                            paint_val = parsed

            desc_text = " ".join(description_parts).strip()
            desc_lower = desc_text.lower()

            # Exclude clear coat adders from both labor and paint
            if "add for clear coat" in desc_lower:
                continue

            # Labor line: must have line number AND valid labor_val
            if line_num and labor_val is not None:
                labor_items.append(
                    {
                        "line": line_num,
                        "description": desc_text,
                        "value": labor_val,
                    }
                )

            # Paint line: must have line number AND valid paint_val
            if line_num and paint_val is not None:
                paint_items.append(
                    {
                        "line": line_num,
                        "description": desc_text,
                        "value": paint_val,
                    }
                )

    return labor_items, paint_items


def process_pdf_grid(pages: List[Dict]) -> Dict[str, Any]:
    """
    Main function to process PDF grid and extract all necessary data.

    Returns a dictionary containing:
        - labor_items: List of labor line items
        - paint_items: List of paint line items
        - total_labor: Total labor hours
        - total_paint: Total paint hours
        - second_ro_line: RO information line
        - vehicle_info_line: Vehicle information line
        - anchor_page, anchor_ymid: Anchor position
        - subtotals_page, subtotals_ymid: Subtotals position
    """
    # Prepare xmid/ymid and page index on words
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            if "xmid" not in w:
                w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            if "ymid" not in w:
                w["ymid"] = (w["y0"] + w["y1"]) / 2.0

    # Detect anchors and vehicle info
    (
        anchor_page,
        anchor_ymid,
        subtotals_page,
        subtotals_ymid,
        second_ro_line,
        vehicle_info_line,
    ) = detect_anchors_and_vehicle_info(pages)

    # Collect words in range (not strictly needed for header detection, but useful for debugging)
    all_words = collect_words_in_range(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    # Detect header columns from header row
    columns = detect_header_columns(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)

    # Extract labor and paint items
    labor_items, paint_items = extract_labor_paint_items(
        pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid
    )

    # Calculate totals
    total_labor = sum(item["value"] for item in labor_items)
    total_paint = sum(item["value"] for item in paint_items)

    print(f"[DEBUG] Columns detected: {columns}")
    print(f"[DEBUG] Total labor items found: {len(labor_items)}")
    print(f"[DEBUG] Total labor hours: {total_labor}")
    print(f"[DEBUG] Total paint items found: {len(paint_items)}")
    print(f"[DEBUG] Total paint hours: {total_paint}")
    if labor_items:
        print(f"[DEBUG] First few labor items: {labor_items[:5]}")
    if paint_items:
        print(f"[DEBUG] First few paint items: {paint_items[:5]}")

    return {
        "labor_items": labor_items,
        "paint_items": paint_items,
        "total_labor": total_labor,
        "total_paint": total_paint,
        "second_ro_line": second_ro_line,
        "vehicle_info_line": vehicle_info_line,
        "anchor_page": anchor_page,
        "anchor_ymid": anchor_ymid,
        "subtotals_page": subtotals_page,
        "subtotals_ymid": subtotals_ymid,
    }


def generate_pages_html(
    pages: List[Dict],
    anchor_page: Optional[int],
    anchor_ymid: Optional[float],
    subtotals_page: Optional[int],
    subtotals_ymid: Optional[float],
    display_w: int = 1200,
) -> str:
    """Generate HTML visualization of PDF pages within the anchor/subtotals range."""
    pages_html = ""

    for pi, page in enumerate(pages, start=1):
        # Skip pages outside range
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
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
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