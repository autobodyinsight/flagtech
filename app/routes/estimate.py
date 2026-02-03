from fastapi import APIRouter, UploadFile, File, Request
import json
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn
from fastapi.responses import JSONResponse

router = APIRouter()


def _ensure_parts_vendors_table(cur) -> None:
    """Create parts_vendors table if it doesn't exist (safety for older DBs)."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_vendors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            domain VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_parts_vendors_domain ON parts_vendors(domain)
        """
    )


def _parse_json_field(value):
    if value is None:
        return []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return []


def _extract_hours(item):
    if not isinstance(item, dict):
        return 0.0
    for key in ("value", "labor", "paint", "hours"):
        val = item.get(key)
        if val is not None:
            try:
                return float(val)
            except Exception:
                return 0.0
    return 0.0

@router.post("/parse-labor", response_model=EstimateResponse)
async def parse_labor(file: UploadFile = File(...)):
    doc = load_pdf(file)
    parsed = parse_estimate_pdf(doc)
    return {"line_items": parsed["labor"]}


@router.post("/parse-paint", response_model=EstimateResponse)
async def parse_paint(file: UploadFile = File(...)):
    doc = load_pdf(file)
    parsed = parse_estimate_pdf(doc)
    return {"line_items": parsed["paint"]}


# ============================================
# TECH MANAGEMENT ENDPOINTS (JSON API)
# ============================================

@router.post("/techs/add")
async def add_tech(request: Request):
    """Add a new technician."""
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()

    try:
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
    """Get list of all active technicians."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, first_name, last_name, pay_rate, active
            FROM techs
            WHERE active = true
            ORDER BY first_name, last_name
        """)
        
        rows = cur.fetchall()
        
        techs = []
        for row in rows:
            techs.append({
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "pay_rate": float(row["pay_rate"]),
                "active": row["active"]
            })
        
        return {"techs": techs}
    finally:
        cur.close()


@router.post("/techs/delete")
async def delete_tech(request: Request):
    """Soft delete a technician (set active=false)."""
    data = await request.json()
    tech_id = data.get("id")

    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "Tech id is required"})

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE techs
            SET active = false
            WHERE id = %s
            RETURNING id
            """,
            (tech_id,),
        )
        row = cur.fetchone()
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "Tech not found"})

        return {"status": "ok", "id": row["id"]}
    finally:
        cur.close()


@router.get("/tech-assignments")
async def tech_assignments(request: Request):
    """Aggregate labor/refinish assignments by tech and RO."""
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT tech, ro, vehicle, total_labor AS total_hours
            FROM labor_assignments
            WHERE tech IS NOT NULL AND tech <> ''
            UNION ALL
            SELECT tech, ro, vehicle, total_paint AS total_hours
            FROM refinish_assignments
            WHERE tech IS NOT NULL AND tech <> ''
            """
        )

        rows = cur.fetchall()

        tech_map = {}
        for row in rows:
            tech = row.get("tech")
            if not tech:
                continue
            ro = row.get("ro") or ""
            vehicle = row.get("vehicle") or ""
            hours = float(row.get("total_hours") or 0)

            tech_entry = tech_map.setdefault(
                tech,
                {
                    "tech": tech,
                    "total_hours": 0.0,
                    "total_vehicles": 0,
                    "ros": {},
                },
            )

            tech_entry["total_hours"] += hours

            if ro not in tech_entry["ros"]:
                tech_entry["ros"][ro] = {
                    "ro": ro,
                    "vehicle_info": vehicle,
                    "total_hours": 0.0,
                }

            tech_entry["ros"][ro]["total_hours"] += hours

        tech_summary = []
        for tech_entry in tech_map.values():
            ros_list = list(tech_entry["ros"].values())
            ros_list.sort(key=lambda r: r["ro"])
            tech_summary.append(
                {
                    "tech": tech_entry["tech"],
                    "total_hours": round(tech_entry["total_hours"], 2),
                    "total_vehicles": len(ros_list),
                    "ros": ros_list,
                }
            )

        tech_summary.sort(key=lambda t: t["tech"])
        return {"tech_summary": tech_summary}
    finally:
        cur.close()


@router.get("/tech-repair-lines")
async def tech_repair_lines(tech: str, ro: str):
    """Return repair lines for a given tech and RO."""
    conn = get_conn()
    cur = conn.cursor()
    lines = []

    try:
        cur.execute(
            """
            SELECT assigned, additional
            FROM labor_assignments
            WHERE tech = %s AND ro = %s
            """,
            (tech, ro),
        )
        for row in cur.fetchall():
            assigned = _parse_json_field(row.get("assigned"))
            additional = _parse_json_field(row.get("additional"))

            if isinstance(assigned, list):
                for item in assigned:
                    desc = (item.get("description") if isinstance(item, dict) else None) or "Labor"
                    lines.append(
                        {
                            "type": "Labor",
                            "description": desc,
                            "hours": _extract_hours(item),
                        }
                    )

            if isinstance(additional, list):
                for item in additional:
                    desc = (item.get("description") if isinstance(item, dict) else None) or "Additional Labor"
                    lines.append(
                        {
                            "type": "Labor",
                            "description": desc,
                            "hours": _extract_hours(item),
                        }
                    )

        cur.execute(
            """
            SELECT assigned, additional
            FROM refinish_assignments
            WHERE tech = %s AND ro = %s
            """,
            (tech, ro),
        )
        for row in cur.fetchall():
            assigned = _parse_json_field(row.get("assigned"))
            additional = _parse_json_field(row.get("additional"))

            if isinstance(assigned, list):
                for item in assigned:
                    desc = (item.get("description") if isinstance(item, dict) else None) or "Refinish"
                    lines.append(
                        {
                            "type": "Refinish",
                            "description": desc,
                            "hours": _extract_hours(item),
                        }
                    )

            if isinstance(additional, list):
                for item in additional:
                    desc = (item.get("description") if isinstance(item, dict) else None) or "Additional Refinish"
                    lines.append(
                        {
                            "type": "Refinish",
                            "description": desc,
                            "hours": _extract_hours(item),
                        }
                    )

        return {"lines": lines}
    finally:
        cur.close()


# ============================================
# PARTS VENDORS ENDPOINTS (JSON API)
# ============================================

@router.post("/vendors/add")
async def add_vendor(request: Request):
    """Add a new parts vendor."""
    data = await request.json()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name:
        return JSONResponse(status_code=400, content={"error": "Vendor name is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        cur.execute(
            """
            INSERT INTO parts_vendors (name, email, phone)
            VALUES (%s, %s, %s)
            RETURNING id, name, email, phone, active
            """,
            (name, email or None, phone or None),
        )

        row = cur.fetchone()
        conn.commit()

        return {
            "vendor": {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "active": row["active"],
            }
        }
    finally:
        cur.close()


@router.get("/vendors/list")
async def list_vendors(request: Request):
    """List active parts vendors."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        cur.execute(
            """
            SELECT id, name, email, phone, active
            FROM parts_vendors
            WHERE active = TRUE
            ORDER BY name
            """
        )

        rows = cur.fetchall()
        vendors = [
            {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "active": row["active"],
            }
            for row in rows
        ]

        return {"vendors": vendors}
    finally:
        cur.close()


@router.get("/dashboard-data")
async def dashboard_data(request: Request):
    """Get aggregated data for the dashboard."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Calculate total sales and pending payments from all ROs
        # Assuming sales = labor hours * rate + parts cost (simplified calculation)
        cur.execute("""
            SELECT 
                SUM(total_labor) as total_labor_hours,
                SUM(total_paint) as total_refinish_hours
            FROM (
                SELECT SUM(total_labor) as total_labor, 0 as total_paint
                FROM labor_assignments
                UNION ALL
                SELECT 0 as total_labor, SUM(total_paint) as total_paint
                FROM refinish_assignments
            ) AS combined
        """)
        
        hours_row = cur.fetchone()
        total_labor_hours = float(hours_row["total_labor_hours"] or 0)
        total_refinish_hours = float(hours_row["total_refinish_hours"] or 0)
        total_hours = total_labor_hours + total_refinish_hours
        
        # Calculate total sales (simplified: $100 per hour as base rate)
        # In production, this should use actual pricing from ROs
        total_sales = total_hours * 100.0
        
        # For pending payments, let's assume 30% of sales are pending (placeholder)
        pending_payments = total_sales * 0.3
        
        # Get count of unique ROs
        cur.execute("""
            SELECT COUNT(DISTINCT ro) as ro_count
            FROM (
                SELECT ro FROM labor_assignments
                UNION
                SELECT ro FROM refinish_assignments
            ) AS all_ros
        """)
        ro_count_row = cur.fetchone()
        ro_count = int(ro_count_row["ro_count"] or 0)
        
        # Calculate average RO
        average_ro = total_sales / ro_count if ro_count > 0 else 0
        
        # Calculate average hours per RO
        average_hrs = total_hours / ro_count if ro_count > 0 else 0
        
        # Calculate current GP (Gross Profit percentage) - placeholder calculation
        # Assuming 40% GP for now
        current_gp = 40.0
        
        # Calculate parts cost - placeholder
        # In production, this should come from actual parts data
        parts_cost = total_sales * 0.3
        
        # Get hours per tech
        cur.execute("""
            SELECT 
                tech,
                SUM(total_hours) as total_hours
            FROM (
                SELECT tech, total_labor as total_hours
                FROM labor_assignments
                WHERE tech IS NOT NULL AND tech <> ''
                UNION ALL
                SELECT tech, total_paint as total_hours
                FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> ''
            ) AS combined
            GROUP BY tech
            ORDER BY total_hours DESC
        """)
        
        hours_per_tech_rows = cur.fetchall()
        hours_per_tech = []
        for row in hours_per_tech_rows:
            hours_per_tech.append({
                "tech": row["tech"],
                "hours": float(row["total_hours"] or 0)
            })
        
        # Get RO count per tech
        cur.execute("""
            SELECT 
                tech,
                COUNT(DISTINCT ro) as ro_count
            FROM (
                SELECT tech, ro FROM labor_assignments
                WHERE tech IS NOT NULL AND tech <> ''
                UNION
                SELECT tech, ro FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> ''
            ) AS combined
            GROUP BY tech
            ORDER BY ro_count DESC
        """)
        
        ros_per_tech_rows = cur.fetchall()
        ros_per_tech = []
        for row in ros_per_tech_rows:
            ros_per_tech.append({
                "tech": row["tech"],
                "ros": int(row["ro_count"] or 0)
            })
        
        cur.close()
        
        return {
            "totalSales": round(total_sales, 2),
            "pendingPayments": round(pending_payments, 2),
            "currentGP": round(current_gp, 2),
            "partsCost": round(parts_cost, 2),
            "averageHrs": round(average_hrs, 2),
            "averageRO": round(average_ro, 2),
            "hoursPerTech": hours_per_tech,
            "rosPerTech": ros_per_tech
        }
    except Exception as e:
        # Return default values on error
        return {
            "totalSales": 0,
            "pendingPayments": 0,
            "currentGP": 0,
            "partsCost": 0,
            "averageHrs": 0,
            "averageRO": 0,
            "hoursPerTech": [],
            "rosPerTech": [],
            "error": str(e)
        }