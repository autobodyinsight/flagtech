from fastapi import APIRouter, UploadFile, File, Request
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
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO techs (first_name, last_name, pay_rate, domain)
            VALUES (%s, %s, %s, %s)
            RETURNING id, first_name, last_name, pay_rate, active, domain
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
    """Get list of all active technicians."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "techs": []})
    
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, first_name, last_name, pay_rate, active
            FROM techs
            WHERE active = true AND domain = %s
            ORDER BY first_name, last_name
        """, (domain,))
        
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
    """List active parts vendors for the user's domain."""
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
        domain = get_user_domain(request)
        if not domain:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
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
                WHERE domain = %s
                UNION ALL
                SELECT 0 as total_labor, SUM(total_paint) as total_paint
                FROM refinish_assignments
                WHERE domain = %s
            ) AS combined
        """, (domain, domain))
        
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
                SELECT ro FROM labor_assignments WHERE domain = %s
                UNION
                SELECT ro FROM refinish_assignments WHERE domain = %s
            ) AS all_ros
        """, (domain, domain))
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
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
                UNION ALL
                SELECT tech, total_paint as total_hours
                FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
            ) AS combined
            GROUP BY tech
            ORDER BY total_hours DESC
        """, (domain, domain))
        
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
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
                UNION
                SELECT tech, ro FROM refinish_assignments
                WHERE tech IS NOT NULL AND tech <> '' AND domain = %s
            ) AS combined
            GROUP BY tech
            ORDER BY ro_count DESC
        """, (domain, domain))
        
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