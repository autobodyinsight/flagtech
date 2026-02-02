"""Upload processing routes for PDF parsing and grid display."""

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import json

from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.services.db import get_conn
from app.services.middleware import get_user_domain

router = APIRouter()

# ============================================================
# UPLOAD + PARSE UI
# ============================================================

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
</body>
</html>
"""


@router.post("/parse", response_class=HTMLResponse)
async def parse_ui(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)

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

# ============================================================
# SAVE LABOR + REFINISH
# ============================================================

@router.post("/save-labor")
async def save_labor(request: Request):
    data = await request.json()
    domain = get_user_domain(request)
    if not domain:
        return {"error": "Not authenticated"}
    conn = get_conn()
    cur = conn.cursor()

    print(f"[save-labor] Saving: tech='{data.get('tech')}', ro='{data.get('ro')}', totalLabor={data.get('totalLabor')}")

    cur.execute("""
        INSERT INTO labor_assignments
        (ro, vehicle, tech, assigned, unassigned, additional, total_labor, total_unassigned, timestamp, domain)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["ro"],
        data["vehicle"],
        data["tech"],
        json.dumps(data["assigned"]),
        json.dumps(data["unassigned"]),
        json.dumps(data["additional"]),
        data["totalLabor"],
        data["totalUnassigned"],
        data["timestamp"],
        domain
    ))

    conn.commit()
    cur.close()
    print(f"[save-labor] Successfully committed to database")
    return {"status": "labor saved"}


@router.post("/save-refinish")
async def save_refinish(request: Request):
    data = await request.json()
    domain = get_user_domain(request)
    if not domain:
        return {"error": "Not authenticated"}
    conn = get_conn()
    cur = conn.cursor()

    print(f"[save-refinish] Saving: tech='{data.get('tech')}', ro='{data.get('ro')}', totalPaint={data.get('totalPaint')}")

    cur.execute("""
        INSERT INTO refinish_assignments
        (ro, vehicle, tech, assigned, unassigned, additional, total_paint, total_unassigned, timestamp, domain)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["ro"],
        data["vehicle"],
        data["tech"],
        json.dumps(data["assigned"]),
        json.dumps(data["unassigned"]),
        json.dumps(data["additional"]),
        data["totalPaint"],
        data["totalUnassigned"],
        data["timestamp"],
        domain
    ))

    conn.commit()
    cur.close()
    print(f"[save-refinish] Successfully committed to database")
    return {"status": "refinish saved"}

