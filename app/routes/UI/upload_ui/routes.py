"""Upload processing routes for PDF parsing and grid display."""

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import kmeans_1d as _kmeans_1d, group_rows as _group_rows
from app.services.db import get_conn
from app.services.middleware import get_user_domain
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

# ============================================================
# TECH MANAGEMENT (Add / List / Delete)
# ============================================================

@router.post("/techs/add")
async def add_tech(request: Request):
    data = await request.json()
    domain = get_user_domain(request)
    if not domain:
        return {"error": "Not authenticated"}
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO techs (first_name, last_name, pay_rate, domain)
            VALUES (%s, %s, %s, %s)
            RETURNING id, first_name, last_name, pay_rate, active
        """, (
            data["first_name"],
            data["last_name"],
            data["pay_rate"],
            domain
        ))

        row = cur.fetchone()
        conn.commit()

        return {
            "tech": {
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "pay_rate": float(row["pay_rate"]),
                "active": row["active"]
            }
        }
    finally:
        cur.close()


@router.get("/techs/list")
async def list_techs(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"error": "Not authenticated", "techs": []}
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, first_name, last_name, pay_rate, active
            FROM techs
            WHERE active = TRUE AND domain = %s
            ORDER BY last_name, first_name
        """, (domain,))

        rows = cur.fetchall()
        techs = [
            {
                "id": r["id"],
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "pay_rate": float(r["pay_rate"]),
                "active": r["active"]
            }
            for r in rows
        ]

        return {"techs": techs}
    finally:
        cur.close()


@router.delete("/techs/{tech_id}")
async def delete_tech(tech_id: int):
    # NOTE: This endpoint is unused in the public UI. Consider adding auth if used.
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE techs SET active = FALSE WHERE id = %s", (tech_id,))
        conn.commit()
        return {"status": "deleted", "tech_id": tech_id}
    finally:
        cur.close()

@router.get("/techs/summary")
async def tech_summary(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"summary": [], "error": "Not authenticated"}
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Labor hours
        cur.execute("""
            SELECT tech,
                   COUNT(DISTINCT ro) AS ro_count,
                   SUM(total_labor) AS total_hours
            FROM labor_assignments
            WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
            GROUP BY tech
        """, (domain,))
        labor_rows = cur.fetchall()

        # Paint hours
        cur.execute("""
            SELECT tech,
                   COUNT(DISTINCT ro) AS ro_count,
                   SUM(total_paint) AS total_hours
            FROM refinish_assignments
            WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
            GROUP BY tech
        """, (domain,))
        paint_rows = cur.fetchall()

        summary = {}

        # Combine labor
        for row in labor_rows:
            tech = row["tech"]
            ro_count = row["ro_count"]
            hours = row["total_hours"]
            if tech not in summary:
                summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0.0}
            summary[tech]["ro_count"] += ro_count
            summary[tech]["hours"] += float(hours or 0)

        # Combine paint
        for row in paint_rows:
            tech = row["tech"]
            ro_count = row["ro_count"]
            hours = row["total_hours"]
            if tech not in summary:
                summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0.0}
            summary[tech]["ro_count"] += ro_count
            summary[tech]["hours"] += float(hours or 0)

        print(f"[tech_summary] Returning {len(summary)} techs: {list(summary.keys())}")
        return {"summary": list(summary.values())}
    except Exception as e:
        print(f"[tech_summary] ERROR: {e}")
        return {"summary": [], "error": str(e)}
    finally:
        cur.close()

@router.get("/techs/{tech}/ros")
async def tech_ro_list(tech: str, request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"ros": [], "error": "Not authenticated"}
    try:
        cur = get_conn().cursor()

        # Labor assignments
        cur.execute("""
            SELECT ro, vehicle, SUM(total_labor) AS hours
            FROM labor_assignments
            WHERE tech = %s AND domain = %s
            GROUP BY ro, vehicle
        """, (tech, domain))
        labor_rows = cur.fetchall()

        # Paint assignments
        cur.execute("""
            SELECT ro, vehicle, SUM(total_paint) AS hours
            FROM refinish_assignments
            WHERE tech = %s AND domain = %s
            GROUP BY ro, vehicle
        """, (tech, domain))
        paint_rows = cur.fetchall()

        ros = {}

        # Merge labor
        for row in labor_rows:
            ro = row["ro"]
            vehicle = row["vehicle"]
            hours = row["hours"]
            if ro not in ros:
                ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0.0}
            ros[ro]["total_hours"] += float(hours or 0)

        # Merge paint
        for row in paint_rows:
            ro = row["ro"]
            vehicle = row["vehicle"]
            hours = row["hours"]
            if ro not in ros:
                ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0.0}
            ros[ro]["total_hours"] += float(hours or 0)

        print(f"[tech_ro_list] Tech: {tech}, ROs: {len(ros)}")
        return {"ros": list(ros.values())}
    except Exception as e:
        print(f"[tech_ro_list] ERROR for tech {tech}: {e}")
        return {"ros": [], "error": str(e)}

@router.get("/techs/{tech}/{ro}/lines")
async def tech_ro_lines(tech: str, ro: str, request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"lines": [], "error": "Not authenticated"}
    try:
        cur = get_conn().cursor()

        # Labor lines
        cur.execute("""
            SELECT assigned
            FROM labor_assignments
            WHERE tech = %s AND ro = %s AND domain = %s
        """, (tech, ro, domain))
        labor_rows = cur.fetchall()

        # Paint lines
        cur.execute("""
            SELECT assigned
            FROM refinish_assignments
            WHERE tech = %s AND ro = %s AND domain = %s
        """, (tech, ro, domain))
        paint_rows = cur.fetchall()

        lines = []

        # Labor
        for row in labor_rows:
            try:
                assigned = json.loads(row["assigned"])
                for item in assigned:
                    lines.append({
                        "line": item.get("line"),
                        "description": item.get("description"),
                        "value": float(item.get("value", 0)),
                        "type": "labor"
                    })
            except Exception as e:
                print(f"[tech_ro_lines] Error parsing labor row: {e}")

        # Paint
        for row in paint_rows:
            try:
                assigned = json.loads(row["assigned"])
                for item in assigned:
                    lines.append({
                        "line": item.get("line"),
                        "description": item.get("description"),
                        "value": float(item.get("value", 0)),
                        "type": "paint"
                    })
            except Exception as e:
                print(f"[tech_ro_lines] Error parsing paint row: {e}")

        print(f"[tech_ro_lines] Tech: {tech}, RO: {ro}, Lines: {len(lines)}")
        return {"lines": lines}
    except Exception as e:
        print(f"[tech_ro_lines] ERROR for tech {tech}, ro {ro}: {e}")
        return {"lines": [], "error": str(e)}

# ============================================================
# RO MANAGEMENT ENDPOINTS
# ============================================================

@router.get("/ros/summary")
async def ro_summary(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"summary": [], "error": "Not authenticated"}
    cur = get_conn().cursor()

    # Get all ROs from labor assignments
    cur.execute("""
        SELECT ro, vehicle, COUNT(DISTINCT tech) AS tech_count, SUM(total_labor) AS total_hours
        FROM labor_assignments
        WHERE ro IS NOT NULL AND ro <> '' AND domain = %s
        GROUP BY ro, vehicle
    """, (domain,))
    labor_rows = cur.fetchall()

    # Get all ROs from refinish assignments
    cur.execute("""
        SELECT ro, vehicle, COUNT(DISTINCT tech) AS tech_count, SUM(total_paint) AS total_hours
        FROM refinish_assignments
        WHERE ro IS NOT NULL AND ro <> '' AND domain = %s
        GROUP BY ro, vehicle
    """, (domain,))
    paint_rows = cur.fetchall()

    summary = {}

    # Combine labor
    for row in labor_rows:
        ro = row["ro"]
        vehicle = row["vehicle"]
        hours = row["total_hours"]
        if ro not in summary:
            summary[ro] = {"ro": ro, "vehicle": vehicle, "tech_count": set(), "total_hours": 0}
        summary[ro]["total_hours"] += float(hours or 0)
        # Will add tech names to set below

    # Combine paint
    for row in paint_rows:
        ro = row["ro"]
        vehicle = row["vehicle"]
        hours = row["total_hours"]
        if ro not in summary:
            summary[ro] = {"ro": ro, "vehicle": vehicle, "tech_count": set(), "total_hours": 0}
        summary[ro]["total_hours"] += float(hours or 0)

    # Get unique tech counts per RO
    for ro in summary:
        cur.execute("""
            SELECT DISTINCT tech FROM (
                SELECT tech FROM labor_assignments WHERE ro = %s AND domain = %s
                UNION
                SELECT tech FROM refinish_assignments WHERE ro = %s AND domain = %s
            ) AS combined_techs
            WHERE tech IS NOT NULL AND tech <> ''
        """, (ro, domain, ro, domain))
        techs = cur.fetchall()
        summary[ro]["tech_count"] = len(techs)

    return {"summary": list(summary.values())}

@router.get("/ros/{ro}/details")
async def ro_details(ro: str, request: Request):
    domain = get_user_domain(request)
    if not domain:
        return {"labor": [], "refinish": [], "error": "Not authenticated"}
    cur = get_conn().cursor()

    # Get labor assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_labor, timestamp
        FROM labor_assignments
        WHERE ro = %s AND domain = %s
        ORDER BY timestamp DESC
    """, (ro, domain))
    labor_rows = cur.fetchall()

    labor = [
        {
            "tech": row["tech"],
            "vehicle": row["vehicle"],
            "assigned": row["assigned"],
            "unassigned": row["unassigned"],
            "additional": row["additional"],
            "total_labor": float(row["total_labor"]),
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
        }
        for row in labor_rows
    ]

    # Get refinish assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_paint, timestamp
        FROM refinish_assignments
        WHERE ro = %s AND domain = %s
        ORDER BY timestamp DESC
    """, (ro, domain))
    paint_rows = cur.fetchall()

    refinish = [
        {
            "tech": row["tech"],
            "vehicle": row["vehicle"],
            "assigned": row["assigned"],
            "unassigned": row["unassigned"],
            "additional": row["additional"],
            "total_paint": float(row["total_paint"]),
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
        }
        for row in paint_rows
    ]

    return {"labor": labor, "refinish": refinish}


# ============================================================
# TECH-RO ASSIGNMENTS ENDPOINTS
# ============================================================

@router.get("/tech-assignments")
async def get_tech_assignments(request: Request):
    """Get all tech-RO assignments with aggregated data for the tech window."""
    domain = get_user_domain(request)
    if not domain:
        return {"assignments": [], "tech_summary": [], "error": "Not authenticated"}
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Get all tech-RO combinations from both labor and refinish
        cur.execute("""
            SELECT 
                tech,
                ro,
                vehicle,
                SUM(labor_hours) AS total_labor,
                SUM(refinish_hours) AS total_refinish
            FROM (
                SELECT 
                    tech,
                    ro,
                    vehicle,
                    total_labor AS labor_hours,
                    0 AS refinish_hours
                FROM labor_assignments
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
                
                UNION ALL
                
                SELECT 
                    tech,
                    ro,
                    vehicle,
                    0 AS labor_hours,
                    total_paint AS refinish_hours
                FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
            ) AS combined
            GROUP BY tech, ro, vehicle
            ORDER BY tech, ro
            """, (domain, domain))
        
        rows = cur.fetchall()
        
        # Build the response
        assignments = []
        tech_summary = {}
        
        for row in rows:
            tech = row["tech"]
            ro = row["ro"]
            vehicle = row["vehicle"]
            labor_hrs = float(row["total_labor"] or 0)
            refinish_hrs = float(row["total_refinish"] or 0)
            total_hrs = labor_hrs + refinish_hrs
            
            # Add to assignments list
            assignments.append({
                "tech": tech,
                "ro": ro,
                "vehicle": vehicle,
                "labor_hours": labor_hrs,
                "refinish_hours": refinish_hrs,
                "total_hours": total_hrs
            })
            
            # Aggregate by tech for summary
            if tech not in tech_summary:
                tech_summary[tech] = {
                    "tech": tech,
                    "total_ros": set(),
                    "total_hours": 0
                }
            tech_summary[tech]["total_ros"].add(ro)
            tech_summary[tech]["total_hours"] += total_hrs
        
        # Convert sets to counts
        for tech in tech_summary:
            tech_summary[tech]["total_vehicles"] = len(tech_summary[tech]["total_ros"])
            del tech_summary[tech]["total_ros"]
        
        return {
            "assignments": assignments,
            "tech_summary": list(tech_summary.values())
        }
        
    except Exception as e:
        print(f"[get_tech_assignments] ERROR: {e}")
        return {"assignments": [], "tech_summary": [], "error": str(e)}
    finally:
        cur.close()


@router.get("/labor-assignments/{ro}")
async def get_labor_assignments(ro: str, request: Request, tech: str = None):
    """Get labor assignment details for a specific RO, optionally filtered by tech."""
    try:
        domain = get_user_domain(request)
        if not domain:
            return {"assignments": [], "error": "Not authenticated"}
        cur = get_conn().cursor()
        
        if tech:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_labor, total_unassigned, timestamp
                FROM labor_assignments
                WHERE ro = %s AND tech = %s AND domain = %s
                ORDER BY timestamp DESC
            """, (ro, tech, domain))
        else:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_labor, total_unassigned, timestamp
                FROM labor_assignments
                WHERE ro = %s AND domain = %s
                ORDER BY timestamp DESC
            """, (ro, domain))
        
        rows = cur.fetchall()
        
        assignments = []
        for row in rows:
            assignments.append({
                "id": row["id"],
                "ro": row["ro"],
                "vehicle": row["vehicle"],
                "tech": row["tech"],
                "assigned": json.loads(row["assigned"]) if row["assigned"] else [],
                "unassigned": json.loads(row["unassigned"]) if row["unassigned"] else [],
                "additional": json.loads(row["additional"]) if row["additional"] else [],
                "total_labor": float(row["total_labor"]),
                "total_unassigned": float(row["total_unassigned"]),
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
            })
        
        return {"assignments": assignments}
        
    except Exception as e:
        print(f"[get_labor_assignments] ERROR for RO {ro}: {e}")
        return {"assignments": [], "error": str(e)}


@router.get("/refinish-assignments/{ro}")
async def get_refinish_assignments(ro: str, request: Request, tech: str = None):
    """Get refinish assignment details for a specific RO, optionally filtered by tech."""
    try:
        domain = get_user_domain(request)
        if not domain:
            return {"assignments": [], "error": "Not authenticated"}
        cur = get_conn().cursor()
        
        if tech:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_paint, total_unassigned, timestamp
                FROM refinish_assignments
                WHERE ro = %s AND tech = %s AND domain = %s
                ORDER BY timestamp DESC
            """, (ro, tech, domain))
        else:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_paint, total_unassigned, timestamp
                FROM refinish_assignments
                WHERE ro = %s AND domain = %s
                ORDER BY timestamp DESC
            """, (ro, domain))
        
        rows = cur.fetchall()
        
        assignments = []
        for row in rows:
            assignments.append({
                "id": row["id"],
                "ro": row["ro"],
                "vehicle": row["vehicle"],
                "tech": row["tech"],
                "assigned": json.loads(row["assigned"]) if row["assigned"] else [],
                "unassigned": json.loads(row["unassigned"]) if row["unassigned"] else [],
                "additional": json.loads(row["additional"]) if row["additional"] else [],
                "total_paint": float(row["total_paint"]),
                "total_unassigned": float(row["total_unassigned"]),
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
            })
        
        return {"assignments": assignments}
        
    except Exception as e:
        print(f"[get_refinish_assignments] ERROR for RO {ro}: {e}")
        return {"assignments": [], "error": str(e)}


# ============================================================
# DEBUG ENDPOINTS
# ============================================================

@router.get("/debug/check-data")
async def check_data():
    """Debug endpoint to check if data is being saved."""
    try:
        cur = get_conn().cursor()
        
        # Check labor assignments
        cur.execute("SELECT COUNT(*) FROM labor_assignments")
        labor_count = cur.fetchone()["count"]
        
        # Check refinish assignments
        cur.execute("SELECT COUNT(*) FROM refinish_assignments")
        refinish_count = cur.fetchone()["count"]
        
        # Get sample techs
        cur.execute("SELECT DISTINCT tech FROM labor_assignments WHERE tech IS NOT NULL LIMIT 5")
        labor_techs = [row["tech"] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT tech FROM refinish_assignments WHERE tech IS NOT NULL LIMIT 5")
        refinish_techs = [row["tech"] for row in cur.fetchall()]
        
        return {
            "labor_assignments_count": labor_count,
            "refinish_assignments_count": refinish_count,
            "sample_labor_techs": labor_techs,
            "sample_refinish_techs": refinish_techs
        }
    except Exception as e:
        return {"error": str(e)}