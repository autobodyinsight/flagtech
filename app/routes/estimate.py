from fastapi import APIRouter, UploadFile, File, Request
import json
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


def _ensure_saved_estimates_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_estimates (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255),
            vehicle TEXT,
            year VARCHAR(10),
            make VARCHAR(50),
            model VARCHAR(50),
            owner_info TEXT,
            insurance_company TEXT,
            claim_number VARCHAR(64),
            phone_original TEXT,
            phone_override TEXT,
            vin VARCHAR(32),
            labor_repairs JSONB,
            paint_repairs JSONB,
            parts_repairs JSONB,
            estimate_totals JSONB,
            parts_total NUMERIC,
            grand_total NUMERIC,
            deductible NUMERIC,
            customer_pay NUMERIC,
            insurance_pay NUMERIC,
            domain VARCHAR(255),
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_repairs JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_totals JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS grand_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS deductible NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS customer_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS owner_info TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_company TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS claim_number VARCHAR(64)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_original TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_override TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS vin VARCHAR(32)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_ro_domain ON saved_estimates(ro, domain)")


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


def _ensure_parts_received_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_received (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            line_id INTEGER NOT NULL,
            vendor VARCHAR(255) NOT NULL,
            cost NUMERIC,
            domain VARCHAR(255) NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_received_ro_domain ON parts_received(ro, domain)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_parts_received_unique ON parts_received(ro, line_id, domain)")


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


def _ensure_ro_assignments_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_assignments (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            excluded_lines JSONB,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_assignments_ro_role_domain
        ON ro_assignments(ro, role, domain)
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


def _parse_float_value(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return 0.0


def _parse_owner_info(owner_info: str) -> tuple[str, str]:
    cleaned = (owner_info or "").strip()
    if not cleaned:
        return "", ""
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    if not lines:
        return "", ""
    name = lines[0]
    phone = lines[1] if len(lines) > 1 else ""
    return name, phone


def _sum_hours(items) -> float:
    if not isinstance(items, list):
        return 0.0
    total = 0.0
    for item in items:
        if not isinstance(item, dict):
            continue
        total += _parse_float_value(item.get("value"))
    return total


def _line_key(item: dict, index: int) -> str:
    line = item.get("line") if isinstance(item, dict) else None
    if line is None or line == "":
        return str(index + 1)
    return str(line)


def _sum_assigned_hours(items, excluded_lines) -> float:
    if not isinstance(items, list):
        return 0.0
    excluded = {str(val) for val in (excluded_lines or [])}
    total = 0.0
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if _line_key(item, idx) in excluded:
            continue
        total += _parse_float_value(item.get("value"))
    return total


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


@router.post("/flash")
async def flash_data():
    """Delete uploaded estimate data across screens."""
    conn = get_conn()
    cur = conn.cursor()

    tables = [
        "parts_received",
        "parts_orders",
        "parts_vendors",
        "ro_notes",
        "ro_phases",
        "estimate_uploads",
        "saved_estimates",
        "techs",
    ]

    deleted_counts = {}
    try:
        for table in tables:
            cur.execute("SELECT to_regclass(%s) AS reg", (table,))
            row = cur.fetchone()
            if not row or not row.get("reg"):
                continue
            cur.execute(f"DELETE FROM {table}")
            deleted_counts[table] = cur.rowcount
        conn.commit()
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})
    finally:
        cur.close()

    return {"status": "success", "deleted": deleted_counts}


@router.get("/dashboard-data")
async def get_dashboard_data(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_assignments_table(cur)
        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                     vehicle,
                     year,
                     make,
                     model,
                   labor_repairs,
                   paint_repairs,
                   parts_repairs,
                   parts_total,
                   grand_total,
                   owner_info,
                   insurance_company,
                   claim_number,
                   phone_original,
                   phone_override
            FROM saved_estimates
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
            """,
            (domain,),
        )
        rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, role, tech_name
            FROM ro_assignments
            WHERE domain = %s
            """,
            (domain,),
        )
        assignment_rows = cur.fetchall()
        assignment_map = {}
        for row in assignment_rows:
            assignment_map[(row.get("ro"), row.get("role"))] = row.get("tech_name")

        total_sales = 0.0
        total_parts = 0.0
        total_hours = 0.0
        ro_list = []
        labor_hours_by_tech = {}
        ros_by_tech = {}

        for row in rows:
            ro = row.get("ro")
            labor_repairs = _parse_json_field(row.get("labor_repairs"))
            paint_repairs = _parse_json_field(row.get("paint_repairs"))
            parts_repairs = _parse_json_field(row.get("parts_repairs"))

            labor_hours = sum(
                _parse_float_value(item.get("value"))
                for item in labor_repairs
                if isinstance(item, dict)
            )
            paint_hours = sum(
                _parse_float_value(item.get("value"))
                for item in paint_repairs
                if isinstance(item, dict)
            )
            ro_hours = labor_hours + paint_hours

            parts_total = _parse_float_value(row.get("parts_total"))
            if parts_total == 0.0 and isinstance(parts_repairs, list):
                parts_total = sum(
                    _parse_float_value(item.get("price")) * _parse_float_value(item.get("qty") or 1)
                    for item in parts_repairs
                    if isinstance(item, dict)
                )

            grand_total = _parse_float_value(row.get("grand_total"))

            total_sales += grand_total
            total_parts += parts_total
            total_hours += ro_hours

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            short_vehicle = " ".join(part for part in (year, make, model) if part)
            vehicle_display = short_vehicle or row.get("vehicle")

            # Parse owner_info to extract customer name and phone
            owner_info = (row.get("owner_info") or "").strip()
            customer_name, customer_phone = _parse_owner_info(owner_info)
            phone_override = (row.get("phone_override") or "").strip()
            phone_original = (row.get("phone_original") or customer_phone).strip()
            current_phone = phone_override or customer_phone

            ro_list.append(
                {
                    "ro": ro,
                    "vehicle": vehicle_display,
                    "customer": customer_name,
                    "phone": current_phone,
                    "phone_original": phone_original,
                    "insurance": row.get("insurance_company") or "",
                    "claim_number": row.get("claim_number") or "",
                    "tech": assignment_map.get((ro, "labor"), "Unassigned"),
                    "painter": assignment_map.get((ro, "paint"), "Unassigned"),
                    "hours": ro_hours,
                    "total": grand_total,
                }
            )

            labor_tech = assignment_map.get((ro, "labor"), "Unassigned")
            if labor_tech:
                labor_hours_by_tech[labor_tech] = labor_hours_by_tech.get(labor_tech, 0.0) + labor_hours
                ros_by_tech[labor_tech] = ros_by_tech.get(labor_tech, 0) + 1

        ro_count = len(rows)
        average_hours = total_hours / ro_count if ro_count else 0.0
        average_ro = total_sales / ro_count if ro_count else 0.0

        hours_per_tech = [
            {"tech": tech, "hours": hours}
            for tech, hours in labor_hours_by_tech.items()
        ]
        hours_per_tech.sort(key=lambda item: item["hours"], reverse=True)

        ros_per_tech = [
            {"tech": tech, "ros": count}
            for tech, count in ros_by_tech.items()
        ]
        ros_per_tech.sort(key=lambda item: item["ros"], reverse=True)

        return {
            "totalSales": total_sales,
            "pendingPayments": 0.0,
            "averageHrs": average_hours,
            "averageRO": average_ro,
            "hoursPerTech": hours_per_tech,
            "rosPerTech": ros_per_tech,
            "roList": ro_list,
        }
    finally:
        cur.close()


@router.post("/ro-phone")
async def update_ro_phone(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    new_phone = (data.get("phone") or "").strip()

    if not ro_value or not new_phone:
        return JSONResponse(status_code=400, content={"error": "ro and phone are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        cur.execute(
            """
            SELECT id, owner_info, phone_original
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        _, parsed_phone = _parse_owner_info(row.get("owner_info") or "")
        phone_original = (row.get("phone_original") or parsed_phone or "").strip()

        cur.execute(
            """
            UPDATE saved_estimates
            SET phone_override = %s,
                phone_original = COALESCE(phone_original, %s)
            WHERE id = %s
            """,
            (new_phone, phone_original, row.get("id")),
        )
        conn.commit()
        return {"status": "success", "phone": new_phone, "phone_original": phone_original}
    finally:
        cur.close()


@router.get("/ro-repairs")
async def get_ro_repairs(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_assignments_table(cur)
        cur.execute(
            """
            SELECT labor_repairs, paint_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        row = cur.fetchone()
        labor_repairs = _parse_json_field(row.get("labor_repairs")) if row else []
        paint_repairs = _parse_json_field(row.get("paint_repairs")) if row else []

        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []

        cur.execute(
            """
            SELECT role, tech_id, tech_name, excluded_lines
            FROM ro_assignments
            WHERE domain = %s AND ro = %s
            """,
            (domain, ro_value),
        )
        assignment_rows = cur.fetchall()
        assignments = {
            "labor": {},
            "paint": {},
        }
        for assignment in assignment_rows:
            role = assignment.get("role")
            if role not in assignments:
                continue
            assignments[role] = {
                "tech_id": assignment.get("tech_id"),
                "tech_name": assignment.get("tech_name"),
                "excluded_lines": assignment.get("excluded_lines") or [],
            }

        return {"labor": labor_repairs, "paint": paint_repairs, "assignments": assignments}
    finally:
        cur.close()


@router.post("/ro-assignments")
async def save_ro_assignments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    role = (data.get("role") or "").strip().lower()
    tech_id = data.get("tech_id")
    tech_name = (data.get("tech_name") or "").strip()
    excluded_lines = data.get("excluded_lines") or []

    if not ro_value or role not in {"labor", "paint"}:
        return JSONResponse(status_code=400, content={"error": "ro and role are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_assignments_table(cur)

        if tech_id and not tech_name:
            cur.execute(
                """
                SELECT first_name, last_name
                FROM techs
                WHERE id = %s
                """,
                (tech_id,),
            )
            row = cur.fetchone()
            if row:
                tech_name = " ".join(part for part in [row.get("first_name"), row.get("last_name")] if part)

        cur.execute(
            """
            INSERT INTO ro_assignments (ro, role, tech_id, tech_name, excluded_lines, domain)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (ro, role, domain)
            DO UPDATE SET
                tech_id = EXCLUDED.tech_id,
                tech_name = EXCLUDED.tech_name,
                excluded_lines = EXCLUDED.excluded_lines,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                ro_value,
                role,
                tech_id,
                tech_name or None,
                json.dumps(excluded_lines),
                domain,
            ),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()


@router.get("/tech-assignments")
async def get_tech_assignments(request: Request, tech_id: int):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "tech_id is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_assignments_table(cur)

        cur.execute(
            """
            SELECT ro, role, excluded_lines
            FROM ro_assignments
            WHERE domain = %s AND tech_id = %s
            """,
            (domain, tech_id),
        )
        assignment_rows = cur.fetchall()

        ros = [row.get("ro") for row in assignment_rows if row.get("ro")]
        if not ros:
            return {"assignments": []}

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   labor_repairs,
                   paint_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = ANY(%s)
            ORDER BY ro, saved_at DESC, id DESC
            """,
            (domain, ros),
        )
        estimate_rows = cur.fetchall()
        repairs_map = {row.get("ro"): row for row in estimate_rows}

        assignments = []
        for row in assignment_rows:
            ro = row.get("ro")
            role = row.get("role")
            excluded_lines = row.get("excluded_lines") or []
            repairs = repairs_map.get(ro) or {}

            if role == "paint":
                items = _parse_json_field(repairs.get("paint_repairs"))
            else:
                items = _parse_json_field(repairs.get("labor_repairs"))

            total_hours = _sum_assigned_hours(items, excluded_lines)
            assignments.append(
                {
                    "ro": ro,
                    "role": role,
                    "total_hours": total_hours,
                    "excluded_lines": excluded_lines,
                }
            )

        return {"assignments": assignments}
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


@router.get("/phase/board")
async def phase_board(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_phases_table(cur)

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                   year,
                   make,
                   model,
                   labor_repairs,
                   paint_repairs
            FROM saved_estimates
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
            """,
            (domain,),
        )
        estimate_rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, phase
            FROM ro_phases
            WHERE domain = %s
            """,
            (domain,),
        )
        phase_rows = cur.fetchall()
        phase_map = {row.get("ro"): row.get("phase") for row in phase_rows}

        items = []
        for row in estimate_rows:
            ro = row.get("ro")
            labor_repairs = _parse_json_field(row.get("labor_repairs"))
            paint_repairs = _parse_json_field(row.get("paint_repairs"))

            labor_hours = _sum_hours(labor_repairs)
            paint_hours = _sum_hours(paint_repairs)

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            short_vehicle = " ".join(part for part in (year, make, model) if part)
            vehicle_display = short_vehicle or row.get("vehicle") or ""

            items.append(
                {
                    "ro": ro,
                    "vehicle": vehicle_display,
                    "phase": phase_map.get(ro, "teardown"),
                    "labor_tech": "Unassigned",
                    "labor_hours": labor_hours,
                    "paint_tech": "Unassigned",
                    "paint_hours": paint_hours,
                }
            )

        return {"items": items}
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
        _ensure_saved_estimates_table(cur)
        _ensure_parts_orders_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                   parts_repairs,
                   saved_at
            FROM saved_estimates
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
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

        cur.execute(
            """
            SELECT ro, COUNT(*) as arrived
            FROM parts_received
            WHERE domain = %s
            GROUP BY ro
            """,
            (domain,),
        )
        received_rows = cur.fetchall()
        received_map = {row["ro"]: int(row.get("arrived") or 0) for row in received_rows}

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
            parts_repairs = _parse_json_field(row.get("parts_repairs"))
            if not isinstance(parts_repairs, list):
                parts_repairs = []

            if not parts_repairs:
                continue

            parts_qty = 0.0
            line_count = 0
            for item in parts_repairs:
                line_count += 1
                qty = item.get("qty") if isinstance(item, dict) else None
                if qty is None:
                    qty = 1
                try:
                    parts_qty += float(qty)
                except (TypeError, ValueError):
                    parts_qty += 1

            summary = order_summary.get(ro, {})
            ros.append(
                {
                    "ro": ro,
                    "vehicle": row.get("vehicle"),
                    "parts_qty": float(parts_qty or line_count or 0),
                    "on_order": summary.get("on_order", 0),
                    "arrival_date": summary.get("arrival_date"),
                    "arrived": received_map.get(ro, 0),
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
        _ensure_saved_estimates_table(cur)
        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro),
        )
        row = cur.fetchone()
        parts_repairs = _parse_json_field(row.get("parts_repairs")) if row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        lines = []
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            lines.append(
                {
                    "id": idx,
                    "line": item.get("line"),
                    "description": item.get("description"),
                    "part_type": item.get("part_type"),
                    "price": float(item.get("price") or 0),
                    "qty": float(item.get("qty") or 0),
                }
            )
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


@router.get("/parts/received")
async def list_parts_received(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_received_table(cur)
        cur.execute(
            """
            SELECT line_id, vendor, cost, received_at
            FROM parts_received
            WHERE ro = %s AND domain = %s
            ORDER BY received_at DESC
            """,
            (ro, domain),
        )
        rows = cur.fetchall()
        items = [
            {
                "line_id": row.get("line_id"),
                "vendor": row.get("vendor"),
                "cost": float(row.get("cost") or 0),
                "received_at": row.get("received_at"),
            }
            for row in rows
        ]
        return {"items": items}
    finally:
        cur.close()


@router.post("/parts/receive")
async def save_parts_received(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro = (data.get("ro") or "").strip()
    items = data.get("items") or []

    if not ro:
        return JSONResponse(status_code=400, content={"error": "RO is required"})
    if not items:
        return JSONResponse(status_code=400, content={"error": "No parts selected"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_received_table(cur)
        cur.execute("DELETE FROM parts_received WHERE ro = %s AND domain = %s", (ro, domain))

        for item in items:
            line_id = item.get("line_id")
            vendor = (item.get("vendor") or "").strip()
            cost = item.get("cost")
            if not line_id or not vendor:
                continue
            cur.execute(
                """
                INSERT INTO parts_received (ro, line_id, vendor, cost, domain)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (ro, line_id, vendor, cost, domain),
            )

        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()