from fastapi import APIRouter, UploadFile, File, Request
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn

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
async def list_techs():
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


@router.get("/tech-assignments")
async def tech_assignments():
    """Get summary of tech assignments (total ROs and hours)."""
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
        cur.close()
        
        # Build the response
        tech_summary_map = {}
        
        for row in rows:
            tech = row["tech"]
            labor_hrs = float(row["total_labor"] or 0)
            refinish_hrs = float(row["total_refinish"] or 0)
            total_hrs = labor_hrs + refinish_hrs
            
            if tech not in tech_summary_map:
                tech_summary_map[tech] = {
                    "tech": tech,
                    "total_vehicles": 0,
                    "total_hours": 0.0
                }
            
            tech_summary_map[tech]["total_vehicles"] += 1
            tech_summary_map[tech]["total_hours"] += total_hrs
        
        tech_summary = list(tech_summary_map.values())
        
        return {
            "tech_summary": tech_summary,
            "error": "0"
        }
    except Exception as e:
        return {
            "tech_summary": [],
            "error": str(e)
        }