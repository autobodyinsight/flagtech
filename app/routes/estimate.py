from fastapi import APIRouter, UploadFile, File, Request
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn
from app.services.middleware import get_user_domain
from fastapi.responses import JSONResponse

router = APIRouter()

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


@router.get("/tech-assignments")
async def tech_assignments(request: Request):
    """Get detailed tech assignments showing each RO."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "assignments": {}})
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        
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
        cur.close()
        
        # Build the response with individual RO assignments
        assignments_by_tech = {}
        
        for row in rows:
            tech = row["tech"]
            ro = row["ro"]
            labor_hrs = float(row["total_labor"] or 0)
            refinish_hrs = float(row["total_refinish"] or 0)
            total_hrs = labor_hrs + refinish_hrs
            
            if tech not in assignments_by_tech:
                assignments_by_tech[tech] = []
            
            assignments_by_tech[tech].append({
                "ro": ro,
                "vehicle": row["vehicle"],
                "total_hours": total_hrs
            })
        
        return {
            "assignments": assignments_by_tech,
            "error": "0"
        }
    except Exception as e:
        return {
            "assignments": {},
            "error": str(e)
        }


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