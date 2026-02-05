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
    from .upload_ui.upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html
    from .upload_ui.labor import get_labor_modal_html, get_labor_modal_styles, get_labor_modal_script
    from .upload_ui.paint import get_refinish_modal_html, get_refinish_modal_styles, get_refinish_modal_script, get_modal_close_handler
    from .upload_ui.save_estimate import get_save_estimate_modal_html, get_save_estimate_modal_styles, get_save_estimate_modal_script
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html
    from labor import get_labor_modal_html, get_labor_modal_styles, get_labor_modal_script
    from paint import get_refinish_modal_html, get_refinish_modal_styles, get_refinish_modal_script, get_modal_close_handler
    from save_estimate import get_save_estimate_modal_html, get_save_estimate_modal_styles, get_save_estimate_modal_script
import math
import re
import json
import hashlib

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


def _parse_vehicle_info(vehicle_info_line: str) -> tuple:
    """Parse year, make, and model from vehicle info line.
    
    Returns:
        (year, make, model) - all as strings or None if not found
    """
    year = None
    make = None
    model = None
    
    if not vehicle_info_line:
        return year, make, model
    
    import re
    # Extract year (4 digits starting with 19 or 20)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', vehicle_info_line)
    if year_match:
        year = year_match.group(1)
    
    # Remove year and extra spaces for make/model parsing
    remaining = vehicle_info_line
    if year_match:
        remaining = vehicle_info_line.replace(year_match.group(0), '').strip()
    
    # Split remaining text - typically: Make Model [trim/body info]
    parts = remaining.split()
    if len(parts) >= 1:
        make = parts[0]
    if len(parts) >= 2:
        model = parts[1]
    
    return year, make, model


def _ensure_estimate_totals_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS estimate_totals (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            vehicle VARCHAR(255),
            year VARCHAR(4),
            make VARCHAR(50),
            model VARCHAR(50),
            labors_total NUMERIC,
            paints_total NUMERIC,
            parts_total NUMERIC,
            grand_total NUMERIC,
            deductible NUMERIC,
            customer_pay NUMERIC,
            insurance_pay NUMERIC,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_estimate_totals_domain ON estimate_totals(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_estimate_totals_ro ON estimate_totals(ro)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_estimate_totals_ro_domain ON estimate_totals(ro, domain)")


def _ensure_repair_lines_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS repair_lines (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            repair_type VARCHAR(50) NOT NULL,
            line_number VARCHAR(50),
            description TEXT,
            labor NUMERIC,
            paint NUMERIC,
            value NUMERIC,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repair_lines_domain ON repair_lines(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repair_lines_ro ON repair_lines(ro)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repair_lines_ro_domain ON repair_lines(ro, domain)")


def _estimate_hash(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

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
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAGOUT</div>
    </div>
    
    <div class="content-area">
        {get_upload_screen_html()}
        {get_estimate_summary_html()}
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
    estimate_totals = result.get("estimate_totals", {})
    second_ro_line = result["second_ro_line"]
    vehicle_info_line = result["vehicle_info_line"]
    anchor_page = result["anchor_page"]
    anchor_ymid = result["anchor_ymid"]
    subtotals_page = result["subtotals_page"]
    subtotals_ymid = result["subtotals_ymid"]

    domain = get_user_domain(request)
    ro_number = None
    if domain:
        ro_match = re.search(r"\bRO\b\s*[:#-]*\s*([A-Za-z0-9-]+)", second_ro_line)
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

    if domain and parts_items and ro_number:
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS parts_lines (
                        id SERIAL PRIMARY KEY,
                        ro VARCHAR(255) NOT NULL,
                        vehicle VARCHAR(255),
                        line_number INTEGER,
                        description TEXT,
                        part_type VARCHAR(50),
                        price NUMERIC,
                        qty NUMERIC,
                        domain VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_lines_domain ON parts_lines(domain)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_lines_ro ON parts_lines(ro)")

                cur.execute("DELETE FROM parts_lines WHERE ro = %s AND domain = %s", (ro_number, domain))

                for item in parts_items:
                    cur.execute(
                        """
                        INSERT INTO parts_lines
                        (ro, vehicle, line_number, description, part_type, price, qty, domain)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            ro_number,
                            vehicle_info_line,
                            item.get("line"),
                            item.get("description"),
                            item.get("part_type"),
                            item.get("price"),
                            item.get("qty"),
                            domain,
                        ),
                    )

                conn.commit()
            finally:
                cur.close()
    
    # Generate pages HTML visualization
    pages_html = generate_pages_html(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)
    
    labor_items_json = json.dumps(labor_items)
    paint_items_json = json.dumps(paint_items)

    # If AJAX request, return just the content without HTML wrapper
    if ajax:
        # Generate modal HTML using imported functions
        labor_modal = get_labor_modal_html(second_ro_line, vehicle_info_line, total_labor)
        refinish_modal = get_refinish_modal_html(second_ro_line, vehicle_info_line, total_paint)
        
        # Generate modal styles
        labor_styles = get_labor_modal_styles()
        refinish_styles = get_refinish_modal_styles()
        save_estimate_styles = get_save_estimate_modal_styles()
        
        # Generate modal scripts
        labor_script = get_labor_modal_script(labor_items_json, total_labor, second_ro_line, vehicle_info_line, ro_number)
        refinish_script = get_refinish_modal_script(paint_items_json, total_paint, second_ro_line, vehicle_info_line, ro_number)
        save_estimate_script = get_save_estimate_modal_script(labor_items_json, paint_items_json, second_ro_line, vehicle_info_line, ro_number, total_labor, total_paint)
        close_handler = get_modal_close_handler()
        
        # Generate save estimate modal HTML
        save_estimate_modal = get_save_estimate_modal_html(second_ro_line, vehicle_info_line, total_labor, total_paint)
        
        content = f"""
<h2>Document Visual Grid</h2>
<button onclick="openLaborModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px; margin-right:10px;'>Assign Labor</button>
<button onclick="openRefinishModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px; margin-right:10px;'>Assign Refinish</button>
<button id="saveSummaryBtn" onclick="openSaveEstimateModal(estimateTotals)" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#4CAF50; color:white; border:none; border-radius:3px;'>Save</button>
<span id="saveStatus" style="margin-left: 10px; color: green;"></span>
<br><br>
{pages_html}
<br><a href='/ui'>Back</a>

{labor_modal}
{refinish_modal}
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
{labor_styles}
{refinish_styles}
{save_estimate_styles}
</style>

<script>
{labor_script}
{refinish_script}
{save_estimate_script}
{close_handler}

// Build estimate totals object with all data (populated from PDF if available)
const estimateTotals = {{
  "parts_total": null,
  "grand_total": null,
  "deductible": null,
  "customer_pay": null,
  "insurance_pay": null
}};
</script>
        """
        return content


@router.post("/save-estimate-totals")
async def save_estimate_totals(request: Request):
    """Legacy endpoint - save estimate totals to database."""
    try:
        data = await request.json()
        domain = get_user_domain(request)
        
        if not domain:
            return {"status": "error", "message": "Domain not found"}
        
        ro = data.get("ro", "").strip()
        if not ro:
            return {"status": "error", "message": "RO number not provided"}
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            _ensure_estimate_totals_table(cur)
            
            # Insert or update the estimate totals
            cur.execute(
                """
                INSERT INTO estimate_totals (ro, vehicle, grand_total, deductible, customer_pay, insurance_pay, domain)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ro, domain)
                DO UPDATE SET 
                    vehicle = EXCLUDED.vehicle,
                    grand_total = EXCLUDED.grand_total,
                    deductible = EXCLUDED.deductible,
                    customer_pay = EXCLUDED.customer_pay,
                    insurance_pay = EXCLUDED.insurance_pay,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    ro,
                    data.get("vehicle"),
                    data.get("grand_total"),
                    data.get("deductible"),
                    data.get("customer_pay"),
                    data.get("insurance_pay"),
                    domain,
                ),
            )
            
            conn.commit()
            return {"status": "success", "message": "Estimate totals saved successfully"}
        
        except Exception as e:
            print(f"[save-estimate-totals] Error: {str(e)}")
            return {"status": "error", "message": f"Database error: {str(e)}"}
        
        finally:
            cur.close()
    
    except Exception as e:
        print(f"[save-estimate-totals] Request error: {str(e)}")
        return {"status": "error", "message": f"Request error: {str(e)}"}


@router.post("/save-estimate")
async def save_estimate(request: Request):
    """Save estimate with repair lines and totals - main save entry point."""
    try:
        data = await request.json()
        domain = get_user_domain(request)
        
        if not domain:
            return {"status": "error", "message": "Domain not found"}
        
        ro = data.get("ro", "").strip()
        if not ro:
            return {"status": "error", "message": "RO number not provided"}
        
        labor_repairs = data.get("labor_repairs", [])
        paint_repairs = data.get("paint_repairs", [])
        estimate_totals = data.get("estimate_totals", {})
        vehicle = data.get("vehicle", "")
        year = data.get("year")
        make = data.get("make")
        model = data.get("model")
        
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Ensure all tables exist
            _ensure_estimate_totals_table(cur)
            _ensure_repair_lines_table(cur)
            
            # Delete existing repair lines for this RO
            cur.execute("DELETE FROM repair_lines WHERE ro = %s AND domain = %s", (ro, domain))
            
            # Insert labor repairs
            for repair in labor_repairs:
                cur.execute(
                    """
                    INSERT INTO repair_lines (ro, repair_type, line_number, description, value, domain)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ro,
                        "labor",
                        repair.get("line"),
                        repair.get("description"),
                        repair.get("value"),
                        domain,
                    ),
                )
            
            # Insert paint repairs
            for repair in paint_repairs:
                cur.execute(
                    """
                    INSERT INTO repair_lines (ro, repair_type, line_number, description, value, domain)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ro,
                        "paint",
                        repair.get("line"),
                        repair.get("description"),
                        repair.get("value"),
                        domain,
                    ),
                )
            
            # Parse vehicle info for year, make, model if not provided
            if not year or not make or not model:
                parsed_year, parsed_make, parsed_model = _parse_vehicle_info(vehicle)
                year = year or parsed_year
                make = make or parsed_make
                model = model or parsed_model
            
            # Save estimate totals
            cur.execute(
                """
                INSERT INTO estimate_totals (ro, vehicle, year, make, model, parts_total, grand_total, deductible, customer_pay, insurance_pay, labors_total, paints_total, domain)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ro, domain)
                DO UPDATE SET 
                    vehicle = EXCLUDED.vehicle,
                    year = EXCLUDED.year,
                    make = EXCLUDED.make,
                    model = EXCLUDED.model,
                    parts_total = EXCLUDED.parts_total,
                    grand_total = EXCLUDED.grand_total,
                    deductible = EXCLUDED.deductible,
                    customer_pay = EXCLUDED.customer_pay,
                    insurance_pay = EXCLUDED.insurance_pay,
                    labors_total = EXCLUDED.labors_total,
                    paints_total = EXCLUDED.paints_total,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    ro,
                    vehicle,
                    year,
                    make,
                    model,
                    estimate_totals.get("parts_total"),
                    estimate_totals.get("grand_total"),
                    estimate_totals.get("deductible"),
                    estimate_totals.get("customer_pay"),
                    estimate_totals.get("insurance_pay"),
                    estimate_totals.get("labors_total"),
                    estimate_totals.get("paints_total"),
                    domain,
                ),
            )
            
            conn.commit()
            return {
                "status": "success",
                "message": f"Estimate saved successfully with {len(labor_repairs)} labor and {len(paint_repairs)} paint repairs",
                "ro": ro
            }
        
        except Exception as e:
            print(f"[save-estimate] Error: {str(e)}")
            conn.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}
        
        finally:
            cur.close()
    
    except Exception as e:
        print(f"[save-estimate] Request error: {str(e)}")
        return {"status": "error", "message": f"Request error: {str(e)}"}


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