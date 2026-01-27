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
    cur.close()

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
    """Get list of all active technicians."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, first_name, last_name, pay_rate, active
        FROM techs
        WHERE active = true
        ORDER BY first_name, last_name
    """)
    
    rows = cur.fetchall()
    cur.close()
    
    techs = []
    for row in rows:
        techs.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "pay_rate": float(row[3]),
            "active": row[4]
        })
    
    return {"techs": techs}


@router.get("/tech-assignments")
async def tech_assignments():
    """Get summary of tech assignments (total ROs and hours)."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Get labor assignments summary
    cur.execute("""
        SELECT 
            tech,
            COUNT(DISTINCT ro) as total_vehicles,
            SUM(CAST(value AS NUMERIC)) as total_hours
        FROM labor_assignments
        WHERE tech IS NOT NULL AND tech != ''
        GROUP BY tech
    """)
    
    labor_rows = cur.fetchall()
    
    # Get refinish assignments summary
    cur.execute("""
        SELECT 
            tech,
            COUNT(DISTINCT ro) as total_vehicles,
            SUM(CAST(value AS NUMERIC)) as total_hours
        FROM refinish_assignments
        WHERE tech IS NOT NULL AND tech != ''
        GROUP BY tech
    """)
    
    refinish_rows = cur.fetchall()
    cur.close()
    
    # Combine results
    tech_summary_map = {}
    
    for row in labor_rows:
        tech = row[0]
        if tech not in tech_summary_map:
            tech_summary_map[tech] = {"tech": tech, "total_vehicles": 0, "total_hours": 0.0}
        tech_summary_map[tech]["total_vehicles"] += int(row[1])
        tech_summary_map[tech]["total_hours"] += float(row[2] or 0)
    
    for row in refinish_rows:
        tech = row[0]
        if tech not in tech_summary_map:
            tech_summary_map[tech] = {"tech": tech, "total_vehicles": 0, "total_hours": 0.0}
        tech_summary_map[tech]["total_vehicles"] += int(row[1])
        tech_summary_map[tech]["total_hours"] += float(row[2] or 0)
    
    tech_summary = list(tech_summary_map.values())
    
    return {
        "tech_summary": tech_summary,
        "error": "0"
    }