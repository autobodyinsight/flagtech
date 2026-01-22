"""Service for processing PDF grids and extracting labor/paint items."""

import re
from typing import List, Dict, Any, Tuple, Optional


def kmeans_1d(values: List[float], k: int, iters: int = 20) -> List[float]:
    """K-means clustering in 1D for column detection."""
    if not values or k <= 0:
        return []
    
    # Initialize centers as quantiles
    vals = sorted(values)
    centers = []
    n = len(vals)
    for i in range(k):
        idx = int((i + 0.5) * n / k)
        centers.append(vals[min(idx, n - 1)])

    for _ in range(iters):
        groups = {i: [] for i in range(k)}
        for v in vals:
            best = min(range(k), key=lambda c: abs(v - centers[c]))
            groups[best].append(v)
        changed = False
        for i in range(k):
            if groups[i]:
                newc = sum(groups[i]) / len(groups[i])
                if abs(newc - centers[i]) > 1e-6:
                    changed = True
                centers[i] = newc
        if not changed:
            break
    return centers


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


def detect_anchors_and_vehicle_info(pages: List[Dict]) -> Tuple[Optional[int], Optional[float], Optional[int], Optional[float], str, str]:
    """
    Detect anchor points in PDF and extract vehicle information.
    
    Returns:
        Tuple of (anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, second_ro_line, vehicle_info_line)
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
                # Capture second RO line and search for vehicle info
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
                    second_ro_line = row_text
                    # Search for vehicle info line (contains 4-digit year)
                    for j in range(idx + 1, min(idx + 10, len(rows))):
                        next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        # Look for a line with a 4-digit year (19xx or 20xx)
                        if re.search(r'\b(19\d{2}|20\d{2})\b', next_line):
                            vehicle_info_line = next_line
                            break
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break
    
    return anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, second_ro_line, vehicle_info_line


def collect_words_in_range(pages: List[Dict], anchor_page: Optional[int], anchor_ymid: Optional[float], 
                           subtotals_page: Optional[int], subtotals_ymid: Optional[float]) -> List[Dict]:
    """Collect all words within the anchor and subtotals range."""
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


def detect_columns(all_words: List[Dict]) -> Dict[str, Optional[float]]:
    """Detect column positions using k-means clustering."""
    xvals = [w["xmid"] for w in all_words]
    centers = kmeans_1d(xvals, 8, iters=40)
    centers_sorted = sorted(centers) if centers else []
    
    print(f"[DEBUG] Column centers detected: {centers_sorted}")
    
    # Identify column positions: 0=Line, 1=Oper, 2=Description, 3=Part Number, 4=Qty, 5=Extended Price, 6=Labor, 7=Paint
    columns = {
        "line": centers_sorted[0] if len(centers_sorted) > 0 else None,
        "oper": centers_sorted[1] if len(centers_sorted) > 1 else None,
        "labor": centers_sorted[6] if len(centers_sorted) > 6 else None,
        "paint": centers_sorted[7] if len(centers_sorted) > 7 else None,
    }
    
    print(f"[DEBUG] Line column X: {columns['line']}, Oper column X: {columns['oper']}, Labor column X: {columns['labor']}, Paint column X: {columns['paint']}")
    
    return columns


def extract_labor_paint_items(pages: List[Dict], columns: Dict[str, Optional[float]], 
                              anchor_page: Optional[int], anchor_ymid: Optional[float],
                              subtotals_page: Optional[int], subtotals_ymid: Optional[float]) -> Tuple[List[Dict], List[Dict]]:
    """Extract labor and paint items from pages."""
    labor_items = []
    paint_items = []
    
    line_col_x = columns["line"]
    oper_col_x = columns["oper"]
    labor_col_x = columns["labor"]
    paint_col_x = columns["paint"]
    
    for pi, page in enumerate(pages, start=1):
        # Skip pages outside range
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue
        
        # Filter words in range
        page_words = []
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)
        
        # Group into rows
        rows = group_rows(page_words, y_thresh=6.0)
        
        # Extract line numbers and labor/paint values from rows
        for row in rows:
            row_words = sorted(row["words"], key=lambda x: x["xmid"])
            line_num = None
            oper = None
            labor_val = None
            paint_val = None
            description = []
            
            for wd in row_words:
                word_xmid = wd.get("xmid", (wd["x0"] + wd["x1"]) / 2.0)
                word_text = wd["text"].strip()
                
                # Check if this is a line number
                if line_col_x and abs(word_xmid - line_col_x) < 40:
                    if re.match(r'^\d{1,3}$', word_text):
                        line_num = word_text
                
                # Check if this is an operation
                if oper_col_x and abs(word_xmid - oper_col_x) < 40:
                    if word_text.lower() in ['r&i', 'rpr', 'repl', 'r&r']:
                        oper = word_text.lower()
                
                # Collect description text
                elif line_col_x and labor_col_x:
                    if line_col_x < word_xmid < labor_col_x - 50:
                        description.append(word_text)
                
                # Check if this is a labor value
                if labor_col_x and abs(word_xmid - labor_col_x) < 40:
                    if re.match(r'^-?\d+\.\d+$', word_text):
                        try:
                            val = float(word_text)
                            if 0.0 <= val <= 99.9:
                                labor_val = val
                        except:
                            pass
                    elif word_text.lower() == 'incl':
                        labor_val = 0.0
                
                # Check if this is a paint value
                if paint_col_x and abs(word_xmid - paint_col_x) < 40:
                    if re.match(r'^-?\d+\.\d+$', word_text):
                        try:
                            val = float(word_text)
                            if 0.0 <= val <= 99.9:
                                paint_val = val
                        except:
                            pass
                    elif word_text.lower() == 'incl':
                        paint_val = 0.0
            
            # Classify repair line
            desc_text = " ".join(description).lower()
            if line_num and "add for clear coat" not in desc_text:
                # Labor only
                if labor_val is not None and paint_val is None:
                    labor_items.append({
                        "line": line_num,
                        "description": " ".join(description),
                        "value": labor_val
                    })
                # Paint only
                elif labor_val is None and paint_val is not None and oper != 'r&i' and paint_val != 0.0:
                    paint_items.append({
                        "line": line_num,
                        "description": " ".join(description),
                        "value": paint_val
                    })
                # Both labor and paint
                elif labor_val is not None and paint_val is not None:
                    labor_items.append({
                        "line": line_num,
                        "description": " ".join(description),
                        "value": labor_val
                    })
                    if oper != 'r&i' and paint_val != 0.0:
                        paint_items.append({
                            "line": line_num,
                            "description": " ".join(description),
                            "value": paint_val
                        })
    
    # Handle CCC collapsed labor column quirk
    labor_has_values = any(item["value"] != 0.0 for item in labor_items)
    paint_has_values = any(item["value"] != 0.0 for item in paint_items)
    
    if not labor_has_values and paint_has_values:
        print("[DEBUG] Service: CCC collapsed labor column → swapping labor and paint")
        labor_items, paint_items = paint_items, labor_items
    
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
    anchor_page, anchor_ymid, subtotals_page, subtotals_ymid, second_ro_line, vehicle_info_line = detect_anchors_and_vehicle_info(pages)
    
    # Collect words in range
    all_words = collect_words_in_range(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)
    
    # Detect columns
    columns = detect_columns(all_words)
    
    # Extract labor and paint items
    labor_items, paint_items = extract_labor_paint_items(pages, columns, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)
    
    # Calculate totals
    total_labor = sum(item["value"] for item in labor_items)
    total_paint = sum(item["value"] for item in paint_items)
    
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
        "subtotals_ymid": subtotals_ymid
    }


def generate_pages_html(pages: List[Dict], anchor_page: Optional[int], anchor_ymid: Optional[float],
                        subtotals_page: Optional[int], subtotals_ymid: Optional[float], display_w: int = 1200) -> str:
    """Generate HTML visualization of PDF pages."""
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
        
        # Filter words in range
        page_words = []
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)
        
        # Display all words
        for wd in page_words:
            x = wd["x0"] * scale
            y = wd["y0"] * scale
            ww = (wd["x1"] - wd["x0"]) * scale
            hh = (wd["y1"] - wd["y0"]) * scale
            txt = wd["text"].replace("<", "&lt;").replace(">", "&gt;")
            boxes_html += f"<div style='position:absolute; left:{x}px; top:{y}px; width:{ww}px; height:{hh}px; font-size:15px; overflow:hidden;'>{txt}</div>"
        
        pages_html += f"<h3>Page {pi}</h3><div style='position:relative; width:{display_w}px; height:{int(h*scale)}px; border:1px solid #ccc; margin-bottom:20px;'>{boxes_html}</div>"
    
    return pages_html
