from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf, extract_words_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import process_pdf_grid, generate_pages_html
from app.services.db import get_conn
from app.services.middleware import get_user_domain
from .flagout import get_flagtech_screen_html
from .parts import get_parts_screen_html, get_parts_script
from .techs import get_techs_screen_html
from .phase import get_phase_screen_html
try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script
    from .upload_ui.save_estimate import (
        get_save_estimate_modal_html,
        get_save_estimate_modal_styles,
        get_save_estimate_modal_script,
    )
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script
    from save_estimate import (
        get_save_estimate_modal_html,
        get_save_estimate_modal_styles,
        get_save_estimate_modal_script,
    )
import math
import re
import json
import hashlib
from datetime import date, timedelta

router = APIRouter()


def _ensure_estimate_uploads_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS estimate_uploads (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            estimate_hash VARCHAR(64) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_estimate_uploads_ro_domain ON estimate_uploads(ro, domain)")


def _ensure_saved_estimates_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_estimates (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255),
            vehicle TEXT,
            year VARCHAR(10),
            make VARCHAR(50),
            model VARCHAR(50),
            owner_info TEXT,
            insurance_company TEXT,
            vin VARCHAR(32),
            claim_number VARCHAR(64),
            phone_original TEXT,
            phone_override TEXT,
            labor_repairs JSONB,
            paint_repairs JSONB,
            parts_repairs JSONB,
            estimate_totals JSONB,
            parts_total NUMERIC,
            grand_total NUMERIC,
            deductible NUMERIC,
            customer_pay NUMERIC,
            insurance_pay NUMERIC,
            in_date DATE DEFAULT CURRENT_DATE,
            ecd_date DATE,
            domain VARCHAR(255),
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_repairs JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_totals JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS grand_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS deductible NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS customer_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS owner_info TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_company TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS vin VARCHAR(32)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS claim_number VARCHAR(64)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_original TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_override TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS ecd_date DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_ro_domain ON saved_estimates(ro, domain)")


def _parse_money(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _estimate_hash(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _safe_json(payload) -> str:
    return json.dumps(payload).replace("<", "\\u003c")


def _weekday_days_from_hours(hours: float) -> int:
    return max(0, math.ceil((hours / 4.0) + 3.0))


def _add_weekdays(start_date: date, weekday_days: int) -> date:
    if weekday_days <= 0:
        return start_date

    current = start_date
    added = 0
    while added < weekday_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def _estimate_hours_for_ecd(payload: dict) -> float:
    labor_repairs = payload.get("labor_repairs") or []
    paint_repairs = payload.get("paint_repairs") or []
    total = 0.0

    def _to_float(value) -> float:
        try:
            return float(str(value).replace(",", ""))
        except Exception:
            return 0.0

    for item in labor_repairs:
        if isinstance(item, dict):
            total += _to_float(item.get("value") or 0)
    for item in paint_repairs:
        if isinstance(item, dict):
            total += _to_float(item.get("value") or 0)
    return total

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
            background-color: #f2f2f2;
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
            background-color: #f2f2f2;
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
        <div class="nav-box" onclick="switchScreen('tech')">TECHS</div>
        <div class="nav-box" onclick="switchScreen('phase')">PHASE</div>
        <div class="nav-box" onclick="switchScreen('parts')">PARTS</div>
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        {get_upload_screen_html()}
        {get_parts_screen_html()}
        {get_techs_screen_html()}
        {get_phase_screen_html()}
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

            if (screenName === 'parts' && typeof partsLoadRos === 'function') {{
                partsLoadRos();
                partsLoadVendors();
            }}

            if (screenName === 'phase' && typeof loadPhaseData === 'function') {{
                loadPhaseData();
            }}

            if (screenName === 'tech' && typeof loadTechsList === 'function') {{
                loadTechsList();
            }}

            if (screenName === 'flagtech' && typeof loadFlagoutTechs === 'function') {{
                loadFlagoutTechs();
            }}
        }}
        
        {get_upload_script()}
        {get_parts_script()}
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
<body style="font-family: Arial; padding: 40px; background-color: #f2f2f2;">
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
<body style="font-family: Arial; padding: 40px; background-color: #f2f2f2;">
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
async def grid_ui(request: Request, file: UploadFile = File(...), ajax: str = None):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # Process PDF using service layer
    result = process_pdf_grid(pages)
    
    # Extract results from service
    labor_items = result["labor_items"]
    paint_items = result["paint_items"]
    parts_items = result.get("parts_items", [])
    total_labor = result["total_labor"]
    total_paint = result["total_paint"]
    parts_total = result.get("parts_total")
    grand_total = result.get("grand_total")
    deductible = result.get("deductible")
    customer_pay = result.get("customer_pay")
    insurance_pay = result.get("insurance_pay")
    second_ro_line = result["second_ro_line"]
    vehicle_info_line = result["vehicle_info_line"]
    owner_info = result.get("owner_info", "")
    insurance_company = result.get("insurance_company", "")
    vin = result.get("vin", "")
    claim_number = result.get("claim_number", "")
    anchor_page = result["anchor_page"]
    anchor_ymid = result["anchor_ymid"]
    subtotals_page = result["subtotals_page"]
    subtotals_ymid = result["subtotals_ymid"]

    domain = get_user_domain(request)
    ro_number = None
    if domain:
        ro_match = re.search(r"\bRO\b.*?(\d+)", second_ro_line)
        ro_number = ro_match.group(1) if ro_match else None

    duplicate_estimate = False

    if domain and ro_number:
        estimate_payload = {
            "labor_items": labor_items,
            "paint_items": paint_items,
            "parts_items": parts_items,
            "total_labor": total_labor,
            "total_paint": total_paint,
            "vehicle": vehicle_info_line,
        }
        estimate_hash = _estimate_hash(estimate_payload)

        conn = get_conn()
        cur = conn.cursor()
        try:
            _ensure_estimate_uploads_table(cur)
            cur.execute(
                """
                SELECT estimate_hash
                FROM estimate_uploads
                WHERE ro = %s AND domain = %s
                """,
                (ro_number, domain),
            )
            row = cur.fetchone()
            if row and row.get("estimate_hash") == estimate_hash:
                duplicate_estimate = True
            else:
                cur.execute(
                    """
                    INSERT INTO estimate_uploads (ro, estimate_hash, domain)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ro, domain)
                    DO UPDATE SET estimate_hash = EXCLUDED.estimate_hash, updated_at = CURRENT_TIMESTAMP
                    """,
                    (ro_number, estimate_hash, domain),
                )
            conn.commit()
        finally:
            cur.close()

    if duplicate_estimate:
        message = "<p style='color:#777;'>Duplicate estimate detected. No changes applied.</p>"
        if ajax:
            return message
        return f"<html><body>{message}<br><a href='/ui'>Back</a></body></html>"

    # Generate pages HTML visualization
    pages_html = generate_pages_html(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)
    
    labor_items_json = _safe_json(labor_items)
    paint_items_json = _safe_json(paint_items)
    parts_items_json = _safe_json(parts_items)

    # If AJAX request, return just the content without HTML wrapper
    if ajax:
        # Generate modal HTML using imported functions
        save_estimate_modal = get_save_estimate_modal_html(
            second_ro_line,
            vehicle_info_line,
            total_labor,
            total_paint,
            parts_total,
            grand_total,
            deductible,
            customer_pay,
            insurance_pay,
            owner_info,
            insurance_company,
            vin,
            claim_number,
        )
        
        # Generate modal styles
        save_estimate_styles = get_save_estimate_modal_styles()
        
        # Generate modal scripts
        save_estimate_script = get_save_estimate_modal_script(
            labor_items_json,
            paint_items_json,
            parts_items_json,
            second_ro_line,
            vehicle_info_line,
            ro_number,
            total_labor,
            total_paint,
            parts_total,
            grand_total,
            deductible,
            customer_pay,
            insurance_pay,
            owner_info,
            insurance_company,
            vin,
            claim_number,
        )
        
        content = f"""
<h2>Document Visual Grid</h2>
<button onclick="openSaveEstimateModal(window.currentEstimateTotals)" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold;'>Save</button>
<br><br>
<div id="estimatePages">
{pages_html}
</div>
<br><a href='/ui'>Back</a>

{save_estimate_modal}

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
        background-color: #f2f2f2;
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
{save_estimate_styles}
</style>

<script>
{save_estimate_script}
</script>
        """
        return content


@router.post("/save-estimate")
async def save_estimate(request: Request):
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()

    ro_value = (data.get("ro_number") or data.get("ro") or "").strip()
    match = re.search(r"\bRO\b\s*[:#-]*\s*([A-Za-z0-9-]+)", ro_value)
    if match:
        ro_value = match.group(1)

    estimate_totals = data.get("estimate_totals") or {}
    domain = get_user_domain(request)
    local_upload_date = (data.get("local_upload_date") or "").strip()
    in_date_value = date.today()
    if local_upload_date:
        try:
            in_date_value = date.fromisoformat(local_upload_date)
        except ValueError:
            in_date_value = date.today()
    ecd_date_value = _add_weekdays(in_date_value, _weekday_days_from_hours(_estimate_hours_for_ecd(data)))

    try:
        _ensure_saved_estimates_table(cur)
        cur.execute(
            """
            INSERT INTO saved_estimates
            (ro, vehicle, year, make, model, owner_info, insurance_company, vin, claim_number,
             labor_repairs, paint_repairs, parts_repairs,
             estimate_totals, parts_total, grand_total, deductible, customer_pay, insurance_pay, in_date, ecd_date, domain)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ro_value,
                data.get("vehicle"),
                data.get("year"),
                data.get("make"),
                data.get("model"),
                data.get("owner_info"),
                data.get("insurance_company"),
                data.get("vin"),
                data.get("claim_number"),
                json.dumps(data.get("labor_repairs") or []),
                json.dumps(data.get("paint_repairs") or []),
                json.dumps(data.get("parts_repairs") or []),
                json.dumps(estimate_totals or {}),
                _parse_money(estimate_totals.get("parts_total")),
                _parse_money(estimate_totals.get("grand_total")),
                _parse_money(estimate_totals.get("deductible")),
                _parse_money(estimate_totals.get("customer_pay")),
                _parse_money(estimate_totals.get("insurance_pay")),
                in_date_value,
                ecd_date_value,
                domain,
            ),
        )
        conn.commit()
    finally:
        cur.close()

    return {"status": "success"}


@router.post("/aligned", response_class=HTMLResponse)
async def aligned_ui(file: UploadFile = File(...)):
    from app.services.grid_processor import kmeans_1d, group_rows
    
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
        rows = group_rows(page.get("words", []), y_thresh=6.0)
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
    centers = kmeans_1d(xvals, 5, iters=40)
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

        rows = group_rows(page.get("words", []), y_thresh=6.0)
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