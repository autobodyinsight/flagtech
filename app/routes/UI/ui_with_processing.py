from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf, extract_words_from_pdf
from app.services.parser import parse_estimate_text
from .shared_utils import kmeans_1d as _kmeans_1d, group_rows as _group_rows
from .flagout import get_flagtech_screen_html
from .ros import get_ros_screen_html
from .techs import get_techs_screen_html
try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script
    from labor import get_labor_modal_html, get_labor_modal_styles, get_labor_modal_script
    from paint import get_refinish_modal_html, get_refinish_modal_styles, get_refinish_modal_script, get_modal_close_handler
import math
import re
import json

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home_screen():
    return f"""
<html>
<head>
    <title>FlagTech</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            background-color: #f5f5f5;
        }}
        .sidebar {{
            width: 150px;
            background-color: #505050;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        .nav-box {{
            padding: 15px;
            background-color: #666666;
            color: white;
            text-align: center;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        .nav-box:hover {{
            background-color: #707070;
            border: 2px solid white;
        }}
        .nav-box.active {{
            background-color: #d32f2f;
            color: white;
            border: 2px solid #d32f2f;
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            margin-left: 150px;
            background-color: white;
            min-height: 100vh;
        }}
        .screen {{
            display: none;
        }}
        .screen.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="nav-box active" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-box" onclick="switchScreen('tech')">TECH'S</div>
        <div class="nav-box" onclick="switchScreen('ros')">RO'S</div>
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        {get_upload_screen_html()}
        {get_techs_screen_html()}
        {get_ros_screen_html()}
        {get_flagtech_screen_html()}
    </div>
    
    <script>
        function switchScreen(screenName) {{
            // Hide all screens
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));
            
            // Remove active class from all nav boxes
            const navBoxes = document.querySelectorAll('.nav-box');
            navBoxes.forEach(box => box.classList.remove('active'));
            
            // Show selected screen
            document.getElementById(screenName).classList.add('active');
            
            // Add active class to clicked nav box
            event.target.classList.add('active');
        }}
        
        {get_upload_script()}
    </script>
</body>
</html>
"""

@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    return """
<html>
<head>
    <title>FlagTech Estimate Parser</title>
</head>
<body style="font-family: Arial; padding: 40px;">
    <h2>Upload an Estimate PDF</h2>
    <form id="uploadForm" action="/ui/grid" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" onchange="this.form.submit()" />
    </form>
    <script>
        // Auto-submit form when file is selected
    </script>
</body>
</html>
"""

@router.post("/parse", response_class=HTMLResponse)
async def parse_ui(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    # Debug logging: show a truncated preview of extracted text
    try:
        print("===EXTRACTED TEXT PREVIEW (truncated)===")
        print(text[:4000])
        print("===END PREVIEW===")
    except Exception:
        print("[extractor] could not print text preview")

    items = parse_estimate_text(text)
    print(f"[parser] parsed {len(items)} items")

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item.line}</td>
            <td>{item.operation or ''}</td>
            <td>{item.description or ''}</td>
            <td>{item.labor if item.labor is not None else ''}</td>
            <td>{item.paint if item.paint is not None else ''}</td>
        </tr>
        """

    return f"""
<html>
<head>
    <title>Parsed Estimate</title>
</head>
<body style="font-family: Arial; padding: 40px;">
    <h2>Parsed Line Items</h2>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Line</th>
            <th>Op</th>
            <th>Description</th>
            <th>Labor</th>
            <th>Paint</th>
        </tr>
        {rows}
    </table>
    <br><br>
    <a href="/ui">Upload another file</a>
</body>
</html>
"""



@router.post("/grid", response_class=HTMLResponse)
async def grid_ui(file: UploadFile = File(...), ajax: str = None):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    display_w = 1200
    # Prepare xmid/ymid and page index on words
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            if "xmid" not in w:
                w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            if "ymid" not in w:
                w["ymid"] = (w["y0"] + w["y1"]) / 2.0

    # detect second RO row (anchor) and ESTIMATE TOTALS row (end marker)
    # also capture second RO line for vehicle info
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    second_ro_line = ""
    vehicle_info_line = ""
    
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
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

    # Collect all words to find column positions
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
    
    # Use k-means to find 8 columns: Line, Oper, Description, Part Number, Qty, Extended Price, Labor, Paint
    xvals = [w["xmid"] for w in all_words]
    centers = _kmeans_1d(xvals, 8, iters=40)
    centers_sorted = sorted(centers) if centers else []
    
    # Debug: print column positions
    print(f"[DEBUG] Column centers detected: {centers_sorted}")
    
    # Identify column positions: 0=Line, 1=Oper, 2=Description, 3=Part Number, 4=Qty, 5=Extended Price, 6=Labor, 7=Paint
    line_col_x = centers_sorted[0] if len(centers_sorted) > 0 else None
    oper_col_x = centers_sorted[1] if len(centers_sorted) > 1 else None
    labor_col_x = centers_sorted[6] if len(centers_sorted) > 6 else None
    paint_col_x = centers_sorted[7] if len(centers_sorted) > 7 else None
    
    print(f"[DEBUG] Line column X: {line_col_x}, Oper column X: {oper_col_x}, Labor column X: {labor_col_x}, Paint column X: {paint_col_x}")

    pages_html = ""
    labor_items = []  # Store items with labor values for the modal
    paint_items = []  # Store items with paint values for the refinish modal
    for pi, page in enumerate(pages, start=1):
        # skip pages before anchor
        if anchor_page and pi < anchor_page:
            continue
        # skip pages after subtotals
        if subtotals_page and pi > subtotals_page:
            continue
        w = page.get("width", 1)
        h = page.get("height", 1)
        scale = display_w / w if w else 1.0

        boxes_html = ""
        
        # First, group words into rows and extract line/labor pairs
        page_words = []
        for wd in page.get("words", []):
            # if this is the anchor page, skip words above the anchor_ymid
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            # if this is the subtotals page, skip words at or below the subtotals_ymid
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)
        
        # Group into rows
        rows = _group_rows(page_words, y_thresh=6.0)
        
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
                
                # Check if this is a line number (max 3 digits in Line column)
                if line_col_x and abs(word_xmid - line_col_x) < 40:
                    if re.match(r'^\d{1,3}$', word_text):
                        line_num = word_text
                
                # Check if this is an operation (r&i, rpr, repl in Oper column)
                if oper_col_x and abs(word_xmid - oper_col_x) < 40:
                    if word_text.lower() in ['r&i', 'rpr', 'repl', 'r&r']:
                        oper = word_text.lower()
                
                # Collect description text (between line and labor columns)
                elif line_col_x and labor_col_x:
                    if line_col_x < word_xmid < labor_col_x - 50:  # Leave space for qty and price columns
                        description.append(word_text)
                
                # Check if this is a labor value in the Labor column
                # Labor format: x.x or xx.x, may be negative, or text "Incl"
                # IMPORTANT: Labor hours must be in range 0.0-99.9 (not prices like 506.78!)
                if labor_col_x and abs(word_xmid - labor_col_x) < 40:
                    # Check for decimal format (positive or negative)
                    if re.match(r'^-?\d+\.\d+$', word_text):
                        try:
                            val = float(word_text)
                            # Only accept values in valid labor hour range (0.0-99.9)
                            if 0.0 <= val <= 99.9:
                                labor_val = val
                        except:
                            pass
                    # Also accept "Incl" as a valid labor indicator
                    elif word_text.lower() == 'incl':
                        labor_val = 0.0  # Represent Incl as 0.0 for tracking purposes
                
                # Check if this is a paint value in the Paint column
                # Paint format: x.x or xx.x, may be negative, or text "Incl"
                # IMPORTANT: Paint hours must be in range 0.0-99.9 (not prices!)
                if paint_col_x and abs(word_xmid - paint_col_x) < 40:
                    # Check for decimal format (positive or negative)
                    if re.match(r'^-?\d+\.\d+$', word_text):
                        try:
                            val = float(word_text)
                            # Only accept values in valid paint hour range (0.0-99.9)
                            if 0.0 <= val <= 99.9:
                                paint_val = val
                        except:
                            pass
                    # Also accept "Incl" as a valid paint indicator
                    elif word_text.lower() == 'incl':
                        paint_val = 0.0  # Represent Incl as 0.0 for tracking purposes
            
            # Classify repair line based on labor/paint presence
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
        
        # Now display all words
        for wd in page_words:
            x = wd["x0"] * scale
            y = wd["y0"] * scale
            ww = (wd["x1"] - wd["x0"]) * scale
            hh = (wd["y1"] - wd["y0"]) * scale
            txt = wd["text"].replace("<", "&lt;").replace(">", "&gt;")
            boxes_html += f"<div style='position:absolute; left:{x}px; top:{y}px; width:{ww}px; height:{hh}px; font-size:15px; overflow:hidden;'>{txt}</div>"

        pages_html += f"<h3>Page {pi}</h3><div style='position:relative; width:{display_w}px; height:{int(h*scale)}px; border:1px solid #ccc; margin-bottom:20px;'>{boxes_html}</div>"

    # UI-side detection of collapsed labor column (CCC quirk)
    labor_has_values = any(item["value"] != 0.0 for item in labor_items)
    paint_has_values = any(item["value"] != 0.0 for item in paint_items)

    if not labor_has_values and paint_has_values:
        print("[DEBUG] UI: CCC collapsed labor column → swapping labor and paint")
        labor_items, paint_items = paint_items, labor_items

    # Now calculate totals using the (possibly swapped) lists
    total_labor = sum(item["value"] for item in labor_items)
    total_paint = sum(item["value"] for item in paint_items)

    labor_items_json = json.dumps(labor_items)
    paint_items_json = json.dumps(paint_items)

    print(f"[DEBUG] Total labor items found: {len(labor_items)}")
    print(f"[DEBUG] Total labor hours: {total_labor}")
    print(f"[DEBUG] Total paint items found: {len(paint_items)}")
    print(f"[DEBUG] Total paint hours: {total_paint}")
    if labor_items:
        print(f"[DEBUG] First few labor items: {labor_items[:5]}")
    if paint_items:
        print(f"[DEBUG] First few paint items: {paint_items[:5]}")

    # If AJAX request, return just the content without HTML wrapper
    if ajax:
        # Generate modal HTML using imported functions
        labor_modal = get_labor_modal_html(second_ro_line, vehicle_info_line, total_labor)
        refinish_modal = get_refinish_modal_html(second_ro_line, vehicle_info_line, total_paint)
        
        # Generate modal styles
        labor_styles = get_labor_modal_styles()
        refinish_styles = get_refinish_modal_styles()
        
        # Generate modal scripts
        labor_script = get_labor_modal_script(labor_items_json, total_labor, second_ro_line, vehicle_info_line)
        refinish_script = get_refinish_modal_script(paint_items_json, total_paint, second_ro_line, vehicle_info_line)
        close_handler = get_modal_close_handler()
        
        content = f"""
<h2>Document Visual Grid</h2>
<button onclick="openLaborModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px; margin-right:10px;'>Assign Labor</button>
<button onclick="openRefinishModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Assign Refinish</button>
<br><br>
{pages_html}
<br><a href='/ui'>Back</a>

{labor_modal}
{refinish_modal}

<style>
  .modal {{
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
  }}
  .modal-content {{
    background-color: #fefefe;
    margin: 2% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 95%;
    max-width: 1400px;
    height: 80vh;
    overflow-y: auto;
    border-radius: 5px;
  }}
  .close {{
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
  }}
  .close:hover {{
    color: black;
  }}
{labor_styles}
{refinish_styles}
</style>

<script>
{labor_script}
{refinish_script}
{close_handler}
</script>
        """
        return content


@router.post("/aligned", response_class=HTMLResponse)
async def aligned_ui(file: UploadFile = File(...)):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # compute xmid/ymid and page index for all words across all pages
    all_words = []
    for pi, page in enumerate(pages, start=1):
        for wdict in page.get("words", []):
            wdict["page_index"] = pi
            wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0
            all_words.append(wdict)

    if not all_words:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # determine anchor (second RO row) and end marker (ESTIMATE TOTALS row)
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
            
            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break

    # collect all xmid values to cluster into 5 columns (global across pages)
    # if anchor found, only use words at/after anchor and before subtotals to compute centers
    if anchor_page:
        if subtotals_page:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page and w["page_index"] < subtotals_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid) or (w["page_index"] == subtotals_page and w["ymid"] <= subtotals_ymid)]
        else:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid)]
    else:
        xvals = [w["xmid"] for w in all_words]
    centers = _kmeans_1d(xvals, 5, iters=40)
    if not centers:
        return "<html><body><p>Could not compute columns.</p><a href='/ui'>Back</a></body></html>"

    centers_sorted = sorted(centers)
    col_names = ["Line", "Op", "Description", "Labor", "Paint"]

    table_rows = ""
    # process pages in order and append their rows
    for page_idx, page in enumerate(pages, start=1):
        # skip pages after subtotals
        if subtotals_page and page_idx > subtotals_page:
            continue
        
        # ensure per-page xmid/ymid are present
        for wdict in page.get("words", []):
            if "xmid" not in wdict:
                wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            if "ymid" not in wdict:
                wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0

        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            # skip rows above anchor (RO) or at/below subtotals
            if anchor_page and page_idx == anchor_page and anchor_ymid is not None:
                if r["ymid"] < anchor_ymid:
                    continue
            if subtotals_page and page_idx == subtotals_page and subtotals_ymid is not None:
                if r["ymid"] >= subtotals_ymid:
                    continue
            
            # sort words in row by x
            wlist = sorted(r["words"], key=lambda ww: ww["xmid"])
            cols = {i: [] for i in range(len(centers_sorted))}
            for ww in wlist:
                # assign to nearest center
                best = min(range(len(centers_sorted)), key=lambda c: abs(ww["xmid"] - centers_sorted[c]))
                cols[best].append(ww)

            # join texts per column
            vals = []
            for i in range(len(centers_sorted)):
                part = " ".join(w["text"] for w in sorted(cols[i], key=lambda z: z["xmid"]))
                vals.append(part)

            # Filter out header/customer rows: require a leading line number in first column
            left_col = vals[0].strip() if vals else ""
            combined_text = " ".join(vals).lower()
            if not re.search(r"\b\d+\b", left_col):
                if any(k in combined_text for k in ("customer", "address", "vin", "page", "estimate", "phone", "fax", "ro")):
                    continue
                if left_col.lower() in ("line", "line#", "no", "qty"):
                    continue

            # render only the five columns
            table_rows += "<tr>"
            for i in range(5):
                table_rows += f"<td>{(vals[i] if i < len(vals) else '')}</td>"
            table_rows += "</tr>"

    header_html = "".join(f"<th>{n}</th>" for n in col_names)

    return f"""
<html>
<head><title>Aligned Table</title></head>
<body style='font-family:Arial; padding:20px;'>
  <h2>Aligned Table (All Pages)</h2>
  <table border='1' cellpadding='6' cellspacing='0'>
    <tr>{header_html}</tr>
    {table_rows}
  </table>
  <br><a href='/ui'>Back</a>
</body>
</html>
"""