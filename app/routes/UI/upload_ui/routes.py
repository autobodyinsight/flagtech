"""Upload processing routes for PDF parsing and grid display."""

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import kmeans_1d as _kmeans_1d, group_rows as _group_rows
from app.services.db import get_conn
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
    cur = get_conn().cursor()

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
    cur = get_conn().cursor()

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
    cur = get_conn().cursor()

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
    cur = get_conn().cursor()
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
    cur = get_conn().cursor()
    cur.execute("UPDATE techs SET active = FALSE WHERE id = %s", (tech_id,))
    conn.commit()
    return {"status": "deleted", "tech_id": tech_id}

@router.get("/techs/summary")
async def tech_summary():
    try:
        cur = get_conn().cursor()

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
        for row in labor_rows:
            tech = row[0]
            ro_count = row[1]
            hours = row[2]
            if tech not in summary:
                summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0.0}
            summary[tech]["ro_count"] += ro_count
            summary[tech]["hours"] += float(hours or 0)

        # Combine paint
        for row in paint_rows:
            tech = row[0]
            ro_count = row[1]
            hours = row[2]
            if tech not in summary:
                summary[tech] = {"tech": tech, "ro_count": 0, "hours": 0.0}
            summary[tech]["ro_count"] += ro_count
            summary[tech]["hours"] += float(hours or 0)

        print(f"[tech_summary] Returning {len(summary)} techs: {list(summary.keys())}")
        return {"summary": list(summary.values())}
    except Exception as e:
        print(f"[tech_summary] ERROR: {e}")
        return {"summary": [], "error": str(e)}

@router.get("/techs/{tech}/ros")
async def tech_ro_list(tech: str):
    try:
        cur = get_conn().cursor()

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
        for row in labor_rows:
            ro = row[0]
            vehicle = row[1]
            hours = row[2]
            if ro not in ros:
                ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0.0}
            ros[ro]["total_hours"] += float(hours or 0)

        # Merge paint
        for row in paint_rows:
            ro = row[0]
            vehicle = row[1]
            hours = row[2]
            if ro not in ros:
                ros[ro] = {"ro": ro, "vehicle": vehicle, "total_hours": 0.0}
            ros[ro]["total_hours"] += float(hours or 0)

        print(f"[tech_ro_list] Tech: {tech}, ROs: {len(ros)}")
        return {"ros": list(ros.values())}
    except Exception as e:
        print(f"[tech_ro_list] ERROR for tech {tech}: {e}")
        return {"ros": [], "error": str(e)}

@router.get("/techs/{tech}/{ro}/lines")
async def tech_ro_lines(tech: str, ro: str):
    try:
        cur = get_conn().cursor()

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
            try:
                assigned = json.loads(row[0])
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
                assigned = json.loads(row[0])
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
async def ro_summary():
    cur = get_conn().cursor()

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
    cur = get_conn().cursor()

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


# ============================================================
# TECH-RO ASSIGNMENTS ENDPOINTS
# ============================================================

@router.get("/tech-assignments")
async def get_tech_assignments():
    """Get all tech-RO assignments with aggregated data for the tech window."""
    try:
        cur = get_conn().cursor()
        
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
                WHERE tech IS NOT NULL AND tech <> ''
                
                UNION ALL
                
                SELECT 
                    tech,
                    ro,
                    vehicle,
                    0 AS labor_hours,
                    total_paint AS refinish_hours
                FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> ''
            ) AS combined
            GROUP BY tech, ro, vehicle
            ORDER BY tech, ro
        """)
        
        rows = cur.fetchall()
        
        # Build the response
        assignments = []
        tech_summary = {}
        
        for row in rows:
            tech = row[0]
            ro = row[1]
            vehicle = row[2]
            labor_hrs = float(row[3] or 0)
            refinish_hrs = float(row[4] or 0)
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
        
        # Convert sets to counts and build ros list
        for tech in tech_summary:
            tech_summary[tech]["total_vehicles"] = len(tech_summary[tech]["total_ros"])
            tech_summary[tech]["ros"] = []
            del tech_summary[tech]["total_ros"]
        
        # Add RO details to tech summary
        for assignment in assignments:
            tech = assignment["tech"]
            if tech in tech_summary:
                ro_data = {
                    "ro": assignment["ro"],
                    "vehicle_info": assignment["vehicle"],
                    "total_hours": assignment["total_hours"]
                }
                tech_summary[tech]["ros"].append(ro_data)
        
        return {
            "assignments": assignments,
            "tech_summary": list(tech_summary.values())
        }
        
    except Exception as e:
        print(f"[get_tech_assignments] ERROR: {e}")
        return {"assignments": [], "tech_summary": [], "error": str(e)}


@router.get("/labor-assignments/{ro}")
async def get_labor_assignments(ro: str, tech: str = None):
    """Get labor assignment details for a specific RO, optionally filtered by tech."""
    try:
        cur = get_conn().cursor()
        
        if tech:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_labor, total_unassigned, timestamp
                FROM labor_assignments
                WHERE ro = %s AND tech = %s
                ORDER BY timestamp DESC
            """, (ro, tech))
        else:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_labor, total_unassigned, timestamp
                FROM labor_assignments
                WHERE ro = %s
                ORDER BY timestamp DESC
            """, (ro,))
        
        rows = cur.fetchall()
        
        assignments = []
        for row in rows:
            assignments.append({
                "id": row[0],
                "ro": row[1],
                "vehicle": row[2],
                "tech": row[3],
                "assigned": json.loads(row[4]) if row[4] else [],
                "unassigned": json.loads(row[5]) if row[5] else [],
                "additional": json.loads(row[6]) if row[6] else [],
                "total_labor": float(row[7]),
                "total_unassigned": float(row[8]),
                "timestamp": row[9].isoformat() if row[9] else None
            })
        
        return {"assignments": assignments}
        
    except Exception as e:
        print(f"[get_labor_assignments] ERROR for RO {ro}: {e}")
        return {"assignments": [], "error": str(e)}


@router.get("/refinish-assignments/{ro}")
async def get_refinish_assignments(ro: str, tech: str = None):
    """Get refinish assignment details for a specific RO, optionally filtered by tech."""
    try:
        cur = get_conn().cursor()
        
        if tech:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_paint, total_unassigned, timestamp
                FROM refinish_assignments
                WHERE ro = %s AND tech = %s
                ORDER BY timestamp DESC
            """, (ro, tech))
        else:
            cur.execute("""
                SELECT id, ro, vehicle, tech, assigned, unassigned, additional, 
                       total_paint, total_unassigned, timestamp
                FROM refinish_assignments
                WHERE ro = %s
                ORDER BY timestamp DESC
            """, (ro,))
        
        rows = cur.fetchall()
        
        assignments = []
        for row in rows:
            assignments.append({
                "id": row[0],
                "ro": row[1],
                "vehicle": row[2],
                "tech": row[3],
                "assigned": json.loads(row[4]) if row[4] else [],
                "unassigned": json.loads(row[5]) if row[5] else [],
                "additional": json.loads(row[6]) if row[6] else [],
                "total_paint": float(row[7]),
                "total_unassigned": float(row[8]),
                "timestamp": row[9].isoformat() if row[9] else None
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
        labor_count = cur.fetchone()[0]
        
        # Check refinish assignments
        cur.execute("SELECT COUNT(*) FROM refinish_assignments")
        refinish_count = cur.fetchone()[0]
        
        # Get sample techs
        cur.execute("SELECT DISTINCT tech FROM labor_assignments WHERE tech IS NOT NULL LIMIT 5")
        labor_techs = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT tech FROM refinish_assignments WHERE tech IS NOT NULL LIMIT 5")
        refinish_techs = [row[0] for row in cur.fetchall()]
        
        return {
            "labor_assignments_count": labor_count,
            "refinish_assignments_count": refinish_count,
            "sample_labor_techs": labor_techs,
            "sample_refinish_techs": refinish_techs
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/tech-repair-lines")
async def get_tech_repair_lines(tech: str, ro: str):
    """Get repair lines assigned to a specific tech for a specific RO."""
    try:
        cur = get_conn().cursor()
        
        lines = []
        
        # Get labor lines for this tech and RO
        cur.execute("""
            SELECT assigned, unassigned, additional
            FROM labor_assignments
            WHERE tech = %s AND ro = %s
            LIMIT 1
        """, (tech, ro))
        
        labor_result = cur.fetchone()
        if labor_result:
            import json
            assigned = json.loads(labor_result[0]) if labor_result[0] else []
            unassigned = json.loads(labor_result[1]) if labor_result[1] else []
            additional = json.loads(labor_result[2]) if labor_result[2] else []
            
            # Add assigned labor lines
            for item in assigned:
                lines.append({
                    "type": "labor",
                    "description": item.get("description", "N/A"),
                    "hours": float(item.get("value", 0))
                })
            
            # Add additional labor hours
            for item in additional:
                lines.append({
                    "type": "labor_additional",
                    "description": item.get("description", "Additional"),
                    "hours": float(item.get("value", 0))
                })
        
        # Get refinish lines for this tech and RO
        cur.execute("""
            SELECT assigned, unassigned, additional
            FROM refinish_assignments
            WHERE tech = %s AND ro = %s
            LIMIT 1
        """, (tech, ro))
        
        refinish_result = cur.fetchone()
        if refinish_result:
            import json
            assigned = json.loads(refinish_result[0]) if refinish_result[0] else []
            unassigned = json.loads(refinish_result[1]) if refinish_result[1] else []
            additional = json.loads(refinish_result[2]) if refinish_result[2] else []
            
            # Add assigned refinish lines
            for item in assigned:
                lines.append({
                    "type": "refinish",
                    "description": item.get("description", "N/A"),
                    "hours": float(item.get("value", 0))
                })
            
            # Add additional refinish hours
            for item in additional:
                lines.append({
                    "type": "refinish_additional",
                    "description": item.get("description", "Additional"),
                    "hours": float(item.get("value", 0))
                })
        
        return {"lines": lines}
    except Exception as e:
        print(f"[get_tech_repair_lines] ERROR: {e}")
        return {"lines": [], "error": str(e)}