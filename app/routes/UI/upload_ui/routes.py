"""Upload processing routes for PDF parsing and grid display."""

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import kmeans_1d as _kmeans_1d, group_rows as _group_rows
from app.services.db import conn
import json

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
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO labor_assignments
        (ro, vehicle, tech, assigned, unassigned, additional, total_labor, total_unassigned, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["ro"],
        data["vehicle"],
        data["tech"],
        json.dumps(data["assigned"]),
        json.dumps(data["unassigned"]),
        json.dumps(data["additional"]),
        data["totalLabor"],
        data["totalUnassigned"],
        data["timestamp"]
    ))

    conn.commit()
    return {"status": "labor saved"}


@router.post("/save-refinish")
async def save_refinish(request: Request):
    data = await request.json()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO refinish_assignments
        (ro, vehicle, tech, assigned, unassigned, additional, total_paint, total_unassigned, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["ro"],
        data["vehicle"],
        data["tech"],
        json.dumps(data["assigned"]),
        json.dumps(data["unassigned"]),
        json.dumps(data["additional"]),
        data["totalPaint"],
        data["totalUnassigned"],
        data["timestamp"]
    ))

    conn.commit()
    return {"status": "refinish saved"}

# ============================================================
# TECH MANAGEMENT (Add / List / Delete)
# ============================================================

@router.post("/techs/add")
async def add_tech(request: Request):
    data = await request.json()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO techs (first_name, last_name, pay_rate)
        VALUES (%s, %s, %s)
        RETURNING id, first_name, last_name, pay_rate, active
    """, (
        data["first_name"],
        data["last_name"],
        data["pay_rate"]
    ))

    row = cur.fetchone()
    conn.commit()

    return {
        "tech": {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "pay_rate": float(row[3]),
            "active": row[4]
        }
    }


@router.get("/techs/list")
async def list_techs():
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name, pay_rate, active
        FROM techs
        WHERE active = TRUE
        ORDER BY last_name, first_name
    """)

    rows = cur.fetchall()
    techs = [
        {
            "id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "pay_rate": float(r[3]),
            "active": r[4]
        }
        for r in rows
    ]

    return {"techs": techs}


@router.delete("/techs/{tech_id}")
async def delete_tech(tech_id: int):
    cur = conn.cursor()
    cur.execute("UPDATE techs SET active = FALSE WHERE id = %s", (tech_id,))
    conn.commit()
    return {"status": "deleted", "tech_id": tech_id}

@router.get("/techs/summary")
async def tech_summary():
    cur = conn.cursor()

    # Labor hours
    cur.execute("""
        SELECT tech,
               COUNT(DISTINCT ro) AS ro_count,
               SUM(total_labor) AS total_hours
        FROM labor_assignments
        WHERE tech IS NOT NULL AND tech <> ''
        GROUP BY tech
    """)
    labor_rows = cur.fetchall()

    # Paint hours
    cur.execute("""
        SELECT tech,
               COUNT(DISTINCT ro) AS ro_count,
               SUM(total_paint) AS total_hours
        FROM refinish_assignments
        WHERE tech IS NOT NULL AND tech <> ''
        GROUP BY tech
    """)
    paint_rows = cur.fetchall()

    summary = {}

    # Combine labor
    for tech, ro_count, hours in labor_rows:
        if tech not in summary:
            summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0}
        summary[tech]["ro_count"] += ro_count
        summary[tech]["hours"] += float(hours or 0)

    # Combine paint
    for tech, ro_count, hours in paint_rows:
        if tech not in summary:
            summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0}
        summary[tech]["ro_count"] += ro_count
        summary[tech]["hours"] += float(hours or 0)

    return {"summary": list(summary.values())}

@router.get("/techs/{tech}/ros")
async def tech_ro_list(tech: str):
    cur = conn.cursor()

    # Labor assignments
    cur.execute("""
        SELECT ro, vehicle, SUM(total_labor) AS hours
        FROM labor_assignments
        WHERE tech = %s
        GROUP BY ro, vehicle
    """, (tech,))
    labor_rows = cur.fetchall()

    # Paint assignments
    cur.execute("""
        SELECT ro, vehicle, SUM(total_paint) AS hours
        FROM refinish_assignments
        WHERE tech = %s
        GROUP BY ro, vehicle
    """, (tech,))
    paint_rows = cur.fetchall()

    ros = {}

    # Merge labor
    for ro, vehicle, hours in labor_rows:
        if ro not in ros:
            ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0}
        ros[ro]["total_hours"] += float(hours or 0)

    # Merge paint
    for ro, vehicle, hours in paint_rows:
        if ro not in ros:
            ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0}
        ros[ro]["total_hours"] += float(hours or 0)

    return {"ros": list(ros.values())}

@router.get("/techs/{tech}/{ro}/lines")
async def tech_ro_lines(tech: str, ro: str):
    cur = conn.cursor()

    # Labor lines
    cur.execute("""
        SELECT assigned
        FROM labor_assignments
        WHERE tech = %s AND ro = %s
    """, (tech, ro))
    labor_rows = cur.fetchall()

    # Paint lines
    cur.execute("""
        SELECT assigned
        FROM refinish_assignments
        WHERE tech = %s AND ro = %s
    """, (tech, ro))
    paint_rows = cur.fetchall()

    lines = []

    # Labor
    for row in labor_rows:
        assigned = json.loads(row[0])
        for item in assigned:
            lines.append({
                "line": item["line"],
                "description": item["description"],
                "value": float(item["value"]),
                "type": "labor"
            })

    # Paint
    for row in paint_rows:
        assigned = json.loads(row[0])
        for item in assigned:
            lines.append({
                "line": item["line"],
                "description": item["description"],
                "value": float(item["value"]),
                "type": "paint"
            })

    return {"lines": lines}

# ============================================================
# RO MANAGEMENT ENDPOINTS
# ============================================================

@router.get("/ros/summary")
async def ro_summary():
    cur = conn.cursor()

    # Get all ROs from labor assignments
    cur.execute("""
        SELECT ro, vehicle, COUNT(DISTINCT tech) AS tech_count, SUM(total_labor) AS total_hours
        FROM labor_assignments
        WHERE ro IS NOT NULL AND ro <> ''
        GROUP BY ro, vehicle
    """)
    labor_rows = cur.fetchall()

    # Get all ROs from refinish assignments
    cur.execute("""
        SELECT ro, vehicle, COUNT(DISTINCT tech) AS tech_count, SUM(total_paint) AS total_hours
        FROM refinish_assignments
        WHERE ro IS NOT NULL AND ro <> ''
        GROUP BY ro, vehicle
    """)
    paint_rows = cur.fetchall()

    summary = {}

    # Combine labor
    for ro, vehicle, tech_count, hours in labor_rows:
        if ro not in summary:
            summary[ro] = {"ro": ro, "vehicle": vehicle, "tech_count": set(), "total_hours": 0}
        summary[ro]["total_hours"] += float(hours or 0)
        # Will add tech names to set below

    # Combine paint
    for ro, vehicle, tech_count, hours in paint_rows:
        if ro not in summary:
            summary[ro] = {"ro": ro, "vehicle": vehicle, "tech_count": set(), "total_hours": 0}
        summary[ro]["total_hours"] += float(hours or 0)

    # Get unique tech counts per RO
    for ro in summary:
        cur.execute("""
            SELECT DISTINCT tech FROM (
                SELECT tech FROM labor_assignments WHERE ro = %s
                UNION
                SELECT tech FROM refinish_assignments WHERE ro = %s
            ) AS combined_techs
            WHERE tech IS NOT NULL AND tech <> ''
        """, (ro, ro))
        techs = cur.fetchall()
        summary[ro]["tech_count"] = len(techs)

    return {"summary": list(summary.values())}

@router.get("/ros/{ro}/details")
async def ro_details(ro: str):
    cur = conn.cursor()

    # Get labor assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_labor, timestamp
        FROM labor_assignments
        WHERE ro = %s
        ORDER BY timestamp DESC
    """, (ro,))
    labor_rows = cur.fetchall()

    labor = [
        {
            "tech": row[0],
            "vehicle": row[1],
            "assigned": row[2],
            "unassigned": row[3],
            "additional": row[4],
            "total_labor": float(row[5]),
            "timestamp": row[6].isoformat() if row[6] else None
        }
        for row in labor_rows
    ]

    # Get refinish assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_paint, timestamp
        FROM refinish_assignments
        WHERE ro = %s
        ORDER BY timestamp DESC
    """, (ro,))
    paint_rows = cur.fetchall()

    refinish = [
        {
            "tech": row[0],
            "vehicle": row[1],
            "assigned": row[2],
            "unassigned": row[3],
            "additional": row[4],
            "total_paint": float(row[5]),
            "timestamp": row[6].isoformat() if row[6] else None
        }
        for row in paint_rows
    ]

    return {"labor": labor, "refinish": refinish}