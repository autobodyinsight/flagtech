from fastapi import APIRouter, UploadFile, File, Request
import json
from datetime import datetime, date, timedelta
import math
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn
from app.services.middleware import get_user_domain
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


def _ensure_parts_lines_table(cur) -> None:
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


def _ensure_parts_orders_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_orders (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            vendor_id INTEGER,
            vendor_name VARCHAR(255),
            arrival_date DATE,
            ordered_lines JSONB,
            arrived_count INTEGER DEFAULT 0,
            returned_count INTEGER DEFAULT 0,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_orders_domain ON parts_orders(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_orders_ro ON parts_orders(ro)")


def _ensure_ro_phases_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_phases (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            phase VARCHAR(50) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_phases_ro_domain ON ro_phases(ro, domain)")


def _ensure_ro_notes_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_notes (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            note TEXT NOT NULL,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_notes_ro_domain ON ro_notes(ro, domain)")


def _parse_json_field(value):
    if value is None:
        return []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return []


def _parse_iso_date(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except Exception:
        return None


def _add_business_days(start_date: date, days: int) -> date:
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


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
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

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
            INSERT INTO parts_vendors (name, email, phone, domain)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, email, phone, active
            """,
            (name, email or None, phone or None, domain),
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
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "vendors": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        cur.execute(
            """
            SELECT id, name, email, phone, active
            FROM parts_vendors
            WHERE active = TRUE AND domain = %s
            ORDER BY name
            """,
            (domain,),
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
        
        # Get detailed RO list
        cur.execute("""
            SELECT 
                ro,
                vehicle,
                tech,
                total_hours,
                total_amount
            FROM (
                SELECT 
                    l.ro,
                    l.vehicle,
                    l.tech,
                    COALESCE(l.total_labor, 0) + COALESCE(r.total_paint, 0) as total_hours,
                    (COALESCE(l.total_labor, 0) + COALESCE(r.total_paint, 0)) * 100 as total_amount
                FROM labor_assignments l
                LEFT JOIN refinish_assignments r ON l.ro = r.ro
                WHERE l.tech IS NOT NULL AND l.tech <> ''
                UNION
                SELECT 
                    r.ro,
                    r.vehicle,
                    r.tech,
                    COALESCE(l.total_labor, 0) + COALESCE(r.total_paint, 0) as total_hours,
                    (COALESCE(l.total_labor, 0) + COALESCE(r.total_paint, 0)) * 100 as total_amount
                FROM refinish_assignments r
                LEFT JOIN labor_assignments l ON r.ro = l.ro
                WHERE r.tech IS NOT NULL AND r.tech <> ''
                AND NOT EXISTS (SELECT 1 FROM labor_assignments WHERE ro = r.ro)
            ) AS combined
            ORDER BY ro DESC
        """)
        
        ro_list_rows = cur.fetchall()
        ro_list = []
        for row in ro_list_rows:
            ro_list.append({
                "ro": row["ro"],
                "vehicle": row["vehicle"],
                "tech": row["tech"],
                "hours": round(float(row["total_hours"] or 0), 2),
                "total": round(float(row["total_amount"] or 0), 2)
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
            "rosPerTech": ros_per_tech,
            "roList": ro_list
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
            "roList": [],
            "error": str(e)
        }


@router.get("/phase-data")
async def phase_data(request: Request):
    """Get RO cards for the Phase board."""
    domain = get_user_domain(request) or "default"
    conn = get_conn()
    cur = conn.cursor()

    try:
        _ensure_ro_phases_table(cur)
        cur.execute(
            """
            SELECT ro,
                   MAX(vehicle) AS vehicle,
                   MAX(tech) AS labor_tech,
                   SUM(COALESCE(total_labor, 0)) AS total_labor,
                   MIN(timestamp) AS first_timestamp
            FROM labor_assignments
            GROUP BY ro
            """
        )
        labor_rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro,
                   MAX(vehicle) AS vehicle,
                   SUM(COALESCE(total_paint, 0)) AS total_paint,
                   MIN(timestamp) AS first_timestamp
            FROM refinish_assignments
            GROUP BY ro
            """
        )
        refinish_rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, phase
            FROM ro_phases
            WHERE domain = %s
            """,
            (domain,),
        )
        phase_rows = cur.fetchall()
        phase_map = {row["ro"]: row["phase"] for row in phase_rows}

        labor_map = {row["ro"]: row for row in labor_rows}
        refinish_map = {row["ro"]: row for row in refinish_rows}

        ro_keys = set(labor_map.keys()) | set(refinish_map.keys())
        today = date.today()
        items = []

        for ro in sorted(ro_keys):
            labor = labor_map.get(ro)
            refinish = refinish_map.get(ro)

            vehicle = None
            tech = None
            labor_hours = 0.0
            refinish_hours = 0.0
            first_timestamp = None

            if labor:
                vehicle = labor.get("vehicle")
                tech = labor.get("labor_tech")
                labor_hours = float(labor.get("total_labor") or 0)
                if labor.get("first_timestamp"):
                    first_timestamp = labor.get("first_timestamp")

            if refinish:
                if not vehicle:
                    vehicle = refinish.get("vehicle")
                refinish_hours = float(refinish.get("total_paint") or 0)
                refinish_ts = refinish.get("first_timestamp")
                if refinish_ts and (not first_timestamp or str(refinish_ts) < str(first_timestamp)):
                    first_timestamp = refinish_ts

            total_hours = labor_hours + refinish_hours
            ecd_days = int(math.ceil(total_hours / 4.0)) + 3
            ecd_date = _add_business_days(today, ecd_days)

            days_in = None
            if first_timestamp:
                if isinstance(first_timestamp, str):
                    parsed = _parse_iso_date(first_timestamp)
                else:
                    try:
                        parsed = first_timestamp.date()
                    except Exception:
                        parsed = None
                if parsed:
                    delta = (today - parsed).days
                    days_in = max(delta, 0)

            items.append(
                {
                    "ro": ro,
                    "vehicle": vehicle,
                    "tech": tech,
                    "labor_hours": round(labor_hours, 2),
                    "total_hours": round(total_hours, 2),
                    "days_in": days_in,
                    "ecd": ecd_date.isoformat(),
                    "phase": phase_map.get(ro, "teardown"),
                }
            )

        return {"items": items}
    finally:
        cur.close()


@router.post("/phase/update")
async def phase_update(request: Request):
    domain = get_user_domain(request) or "default"
    data = await request.json()
    ro = (data.get("ro") or "").strip()
    phase = (data.get("phase") or "").strip().lower()

    if not ro or not phase:
        return JSONResponse(status_code=400, content={"error": "ro and phase are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_phases_table(cur)
        cur.execute(
            """
            INSERT INTO ro_phases (ro, phase, domain)
            VALUES (%s, %s, %s)
            ON CONFLICT (ro, domain)
            DO UPDATE SET phase = EXCLUDED.phase, updated_at = CURRENT_TIMESTAMP
            """,
            (ro, phase, domain),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()


@router.get("/ro-notes")
async def list_ro_notes(request: Request, ro: str):
    domain = get_user_domain(request) or "default"
    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_notes_table(cur)
        cur.execute(
            """
            SELECT note, created_at
            FROM ro_notes
            WHERE ro = %s AND domain = %s
            ORDER BY created_at DESC
            """,
            (ro, domain),
        )
        rows = cur.fetchall()
        notes = [
            {"note": row.get("note"), "created_at": row.get("created_at")}
            for row in rows
        ]
        return {"notes": notes}
    finally:
        cur.close()


@router.post("/ro-notes")
async def add_ro_note(request: Request):
    domain = get_user_domain(request) or "default"
    data = await request.json()
    ro = (data.get("ro") or "").strip()
    note = (data.get("note") or "").strip()
    if not ro or not note:
        return JSONResponse(status_code=400, content={"error": "ro and note are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_notes_table(cur)
        cur.execute(
            """
            INSERT INTO ro_notes (ro, note, domain)
            VALUES (%s, %s, %s)
            """,
            (ro, note, domain),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()


# ============================================
# PARTS MANAGEMENT ENDPOINTS (JSON API)
# ============================================

@router.get("/parts/ros")
async def list_parts_ros(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "ros": []})

    conn = get_conn()
    cur = conn.cursor()

    try:
        _ensure_parts_lines_table(cur)
        _ensure_parts_orders_table(cur)

        cur.execute(
            """
            SELECT ro,
                   MAX(vehicle) as vehicle,
                   SUM(COALESCE(qty, 1)) as parts_qty,
                   COUNT(*) as line_count
            FROM parts_lines
            WHERE domain = %s
            GROUP BY ro
            ORDER BY ro
            """,
            (domain,),
        )
        rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, arrival_date, ordered_lines, arrived_count, returned_count, created_at
            FROM parts_orders
            WHERE domain = %s
            ORDER BY created_at DESC
            """,
            (domain,),
        )
        orders = cur.fetchall()

        order_summary = {}
        for order in orders:
            ro = order["ro"]
            if ro not in order_summary:
                order_summary[ro] = {
                    "on_order": 0,
                    "arrival_date": order.get("arrival_date"),
                    "arrived": 0,
                    "returned": 0,
                }

            ordered_lines = order.get("ordered_lines") or []
            try:
                ordered_count = len(ordered_lines)
            except Exception:
                ordered_count = 0

            order_summary[ro]["on_order"] += ordered_count
            order_summary[ro]["arrived"] += int(order.get("arrived_count") or 0)
            order_summary[ro]["returned"] += int(order.get("returned_count") or 0)

        ros = []
        for row in rows:
            ro = row["ro"]
            summary = order_summary.get(ro, {})
            ros.append(
                {
                    "ro": ro,
                    "vehicle": row.get("vehicle"),
                    "parts_qty": float(row.get("parts_qty") or row.get("line_count") or 0),
                    "on_order": summary.get("on_order", 0),
                    "arrival_date": summary.get("arrival_date"),
                    "arrived": summary.get("arrived", 0),
                    "returned": summary.get("returned", 0),
                }
            )

        return {"ros": ros}
    finally:
        cur.close()


@router.get("/parts/ro-lines")
async def list_parts_lines(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "lines": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_lines_table(cur)
        cur.execute(
            """
            SELECT id, line_number, description, part_type, price, qty
            FROM parts_lines
            WHERE domain = %s AND ro = %s
            ORDER BY line_number NULLS LAST, id
            """,
            (domain, ro),
        )
        rows = cur.fetchall()
        lines = [
            {
                "id": row["id"],
                "line": row.get("line_number"),
                "description": row.get("description"),
                "part_type": row.get("part_type"),
                "price": float(row.get("price") or 0),
                "qty": float(row.get("qty") or 0),
            }
            for row in rows
        ]
        return {"lines": lines}
    finally:
        cur.close()


@router.post("/parts/order")
async def save_parts_order(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro = data.get("ro")
    vendor_id = data.get("vendor_id")
    vendor_name = data.get("vendor_name")
    arrival_date = data.get("arrival_date")
    ordered_lines = data.get("ordered_lines") or []

    if not ro:
        return JSONResponse(status_code=400, content={"error": "RO is required"})
    if not ordered_lines:
        return JSONResponse(status_code=400, content={"error": "No parts selected"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_orders_table(cur)

        if vendor_id and not vendor_name:
            _ensure_parts_vendors_table(cur)
            cur.execute(
                "SELECT name FROM parts_vendors WHERE id = %s AND domain = %s",
                (vendor_id, domain),
            )
            row = cur.fetchone()
            vendor_name = row["name"] if row else None

        cur.execute(
            """
            INSERT INTO parts_orders
            (ro, vendor_id, vendor_name, arrival_date, ordered_lines, domain)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                ro,
                vendor_id,
                vendor_name,
                arrival_date,
                json.dumps(ordered_lines),
                domain,
            ),
        )
        conn.commit()
        return {"status": "saved"}
    finally:
        cur.close()