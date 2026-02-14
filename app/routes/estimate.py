from fastapi import APIRouter, UploadFile, File, Request
import json
import math
from datetime import date, datetime, timedelta
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
            in_date DATE DEFAULT CURRENT_DATE,
            ecd_date DATE,
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
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS ecd_date DATE")
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
            assigned_hours NUMERIC,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_assignments ADD COLUMN IF NOT EXISTS assigned_hours NUMERIC")
    
    # Check if unique index exists
    cur.execute(
        """
        SELECT indexname FROM pg_indexes 
        WHERE indexname = 'idx_ro_assignments_ro_role_domain'
        """
    )
    index_exists = cur.fetchone()
    
    if not index_exists:
        # Clean up duplicates before creating unique index
        # Keep the most recent record for each (ro, role, domain) combination
        cur.execute(
            """
            DELETE FROM ro_assignments a
            WHERE id NOT IN (
                SELECT MAX(id) FROM ro_assignments
                GROUP BY ro, role, domain
            )
            """
        )
        
        # Now create the unique index
        cur.execute(
            """
            CREATE UNIQUE INDEX idx_ro_assignments_ro_role_domain
            ON ro_assignments(ro, role, domain)
            """
        )


def _ensure_ro_line_assignments_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_line_assignments (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            repair_type VARCHAR(20) NOT NULL,
            line_key VARCHAR(64) NOT NULL,
            line_number VARCHAR(64),
            description TEXT,
            hours NUMERIC,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            source_repair_type VARCHAR(20),
            is_pending BOOLEAN DEFAULT FALSE,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS is_pending BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS source_repair_type VARCHAR(20)")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS ready_to_flag BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS flagged_at TIMESTAMP")
    cur.execute(
        """
        UPDATE ro_line_assignments
        SET source_repair_type = repair_type
        WHERE source_repair_type IS NULL OR source_repair_type = ''
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_line_assignments_unique
        ON ro_line_assignments(ro, repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_line_assignments_source_unique
        ON ro_line_assignments(ro, source_repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_line_assignments_ro_domain
        ON ro_line_assignments(ro, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_line_assignments_ready_flag
        ON ro_line_assignments(domain, tech_id, ready_to_flag)
        """
    )


def _ensure_ro_flagout_lines_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_flagout_lines (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            repair_type VARCHAR(20) NOT NULL,
            line_key VARCHAR(64) NOT NULL,
            line_number VARCHAR(64),
            description TEXT,
            hours NUMERIC,
            pay_rate NUMERIC,
            pay_amount NUMERIC,
            status VARCHAR(32) NOT NULL DEFAULT 'ready_to_flag',
            domain VARCHAR(255) NOT NULL,
            flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_rate NUMERIC")
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_amount NUMERIC")
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_flagout_lines_unique
        ON ro_flagout_lines(ro, tech_id, repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_flagout_lines_domain_status
        ON ro_flagout_lines(domain, status, flagged_at)
        """
    )


def _ensure_techs_table(cur) -> None:
    """Create techs table if it doesn't exist."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS techs (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            pay_rate NUMERIC(10, 2) NOT NULL,
            domain VARCHAR(255),
            active BOOLEAN DEFAULT TRUE,
            status VARCHAR(32) DEFAULT 'Active',
            role VARCHAR(100) DEFAULT '',
            total_ros INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'Active'")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS role VARCHAR(100) DEFAULT ''")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS total_ros INTEGER DEFAULT 0")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_techs_domain ON techs(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_techs_active ON techs(active)")


def _ensure_archived_techs_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS archived_techs (
            id SERIAL PRIMARY KEY,
            tech_id INTEGER NOT NULL,
            tech_name VARCHAR(255) NOT NULL,
            pay_rate NUMERIC(10, 2),
            assigned_ros JSONB,
            total_hours NUMERIC,
            domain VARCHAR(255),
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS assigned_ros JSONB")
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS total_hours NUMERIC")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_archived_techs_domain_archived ON archived_techs(domain, archived_at DESC)")


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


def _coerce_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return datetime.fromisoformat(cleaned).date()
        except Exception:
            return None
    return None


def _weekday_days_from_hours(hours: float) -> int:
    return max(0, math.ceil((hours / 4.0) + 3.0))


def _add_weekdays(start_date: date, weekday_days: int) -> date:
    if weekday_days <= 0:
        return start_date

    current = start_date
    added = 0
    while added < weekday_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def _calculate_ecd_date(in_date: date | None, hours: float) -> date | None:
    if in_date is None:
        return None
    return _add_weekdays(in_date, _weekday_days_from_hours(hours))


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


def _normalize_repair_type(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized == "labor":
        return "body"
    if normalized in {"body", "paint", "mech", "frame"}:
        return normalized
    return "body"


def _load_latest_repairs_for_ro(cur, domain: str, ro_value: str) -> tuple[list, list]:
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
    row = cur.fetchone() or {}
    labor_repairs = _parse_json_field(row.get("labor_repairs"))
    paint_repairs = _parse_json_field(row.get("paint_repairs"))
    if not isinstance(labor_repairs, list):
        labor_repairs = []
    if not isinstance(paint_repairs, list):
        paint_repairs = []
    return labor_repairs, paint_repairs


def _upsert_ro_lines(cur, domain: str, ro_value: str, repair_type: str, lines: list) -> None:
    normalized_type = _normalize_repair_type(repair_type)
    if not isinstance(lines, list):
        return
    for idx, item in enumerate(lines):
        if not isinstance(item, dict):
            continue
        line_key = _line_key(item, idx)
        line_number = str(item.get("line") or line_key)
        description = (item.get("description") or "").strip()
        hours = _parse_float_value(item.get("value"))
        cur.execute(
            """
            INSERT INTO ro_line_assignments (
                ro,
                repair_type,
                source_repair_type,
                line_key,
                line_number,
                description,
                hours,
                tech_id,
                tech_name,
                is_pending,
                domain
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, FALSE, %s)
            ON CONFLICT (ro, source_repair_type, line_key, domain)
            DO UPDATE SET
                line_number = EXCLUDED.line_number,
                description = EXCLUDED.description,
                hours = EXCLUDED.hours,
                updated_at = CURRENT_TIMESTAMP
            """,
            (ro_value, normalized_type, normalized_type, line_key, line_number, description, hours, domain),
        )


def _ensure_ro_line_assignments_for_ro(cur, domain: str, ro_value: str) -> None:
    labor_repairs, paint_repairs = _load_latest_repairs_for_ro(cur, domain, ro_value)
    _upsert_ro_lines(cur, domain, ro_value, "body", labor_repairs)
    _upsert_ro_lines(cur, domain, ro_value, "paint", paint_repairs)


def _get_scope_rows(cur, domain: str, ro_value: str, source: dict) -> list:
    mode = (source.get("mode") or "").strip().lower()
    if mode == "unassigned":
        repair_type = _normalize_repair_type(source.get("repair_type"))
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NULL
              AND COALESCE(is_pending, FALSE) = FALSE
              AND repair_type = %s
            """,
            (domain, ro_value, repair_type),
        )
        return cur.fetchall()

    if mode == "pending":
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NULL
              AND COALESCE(is_pending, FALSE) = TRUE
            """,
            (domain, ro_value),
        )
        return cur.fetchall()

    if mode == "tech":
        repair_type = _normalize_repair_type(source.get("repair_type"))
        tech_name = (source.get("tech_name") or "").strip()
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name = %s
              AND repair_type = %s
            """,
            (domain, ro_value, tech_name, repair_type),
        )
        return cur.fetchall()

    return []


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
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()

    try:
        _ensure_techs_table(cur)
        cur.execute("""
            INSERT INTO techs (first_name, last_name, pay_rate, domain, status, role, total_ros)
            VALUES (%s, %s, %s, %s, 'Active', '', 0)
            RETURNING id, first_name, last_name, pay_rate, active, status, role, total_ros
        """, (
            data["first_name"],
            data["last_name"],
            data["pay_rate"],
            domain,
        ))

        row = cur.fetchone()
        conn.commit()

        return {
            "tech": {
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "pay_rate": float(row["pay_rate"]),
                "active": row["active"],
                "status": row.get("status") or "Active",
                "role": row.get("role") or "",
                "total_ros": int(row.get("total_ros") or 0),
            }
        }
    finally:
        cur.close()


@router.get("/techs/list")
async def list_techs(request: Request):
    """Get list of all active technicians."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    
    try:
        _ensure_techs_table(cur)
        _ensure_ro_line_assignments_table(cur)

        cur.execute("""
                        SELECT
                                t.id,
                                t.first_name,
                                t.last_name,
                                t.pay_rate,
                                t.active,
                                t.status,
                                t.role,
                                COALESCE(rc.total_ros, 0) AS total_ros
                        FROM techs t
                        LEFT JOIN (
                                SELECT tech_id, COUNT(DISTINCT ro) AS total_ros
                                FROM ro_line_assignments
                                WHERE domain = %s
                                    AND COALESCE(ready_to_flag, FALSE) = FALSE
                                    AND tech_id IS NOT NULL
                                GROUP BY tech_id
                        ) rc ON rc.tech_id = t.id
                        WHERE t.active = true
                            AND (t.domain = %s OR t.domain IS NULL)
            ORDER BY first_name, last_name
                """, (domain, domain))
        
        rows = cur.fetchall()
        
        techs = []
        for row in rows:
            techs.append({
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "pay_rate": float(row["pay_rate"]),
                "active": row["active"],
                "status": row.get("status") or "Active",
                "role": row.get("role") or "",
                "total_ros": int(row.get("total_ros") or 0),
            })
        
        return {"techs": techs}
    finally:
        cur.close()


@router.post("/techs/status")
async def update_tech_status(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    tech_id = data.get("id")
    status_value = (data.get("status") or "").strip()
    allowed = {"Active", "Vacation", "FMLA"}
    if not tech_id or status_value not in allowed:
        return JSONResponse(status_code=400, content={"error": "id and valid status are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_techs_table(cur)
        cur.execute(
            """
            UPDATE techs
            SET status = %s
            WHERE id = %s
              AND active = TRUE
              AND (domain = %s OR domain IS NULL)
            RETURNING id, status
            """,
            (status_value, tech_id, domain),
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            return JSONResponse(status_code=404, content={"error": "Tech not found"})
        return {"status": "ok", "tech": {"id": row.get("id"), "status": row.get("status")}}
    finally:
        cur.close()


@router.post("/techs/update")
async def update_tech_line(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    tech_id = data.get("id")
    role_value = (data.get("role") or "").strip()
    pay_rate_raw = data.get("pay_rate")

    allowed_roles = {"Body", "Paint", "Mech"}
    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "id is required"})
    if role_value not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "role must be Body, Paint, or Mech"})

    try:
        pay_rate_value = float(pay_rate_raw)
    except Exception:
        return JSONResponse(status_code=400, content={"error": "pay_rate must be numeric"})

    if pay_rate_value <= 0:
        return JSONResponse(status_code=400, content={"error": "pay_rate must be greater than zero"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_techs_table(cur)
        cur.execute(
            """
            UPDATE techs
            SET role = %s,
                pay_rate = %s
            WHERE id = %s
              AND active = TRUE
              AND (domain = %s OR domain IS NULL)
            RETURNING id, role, pay_rate
            """,
            (role_value, pay_rate_value, tech_id, domain),
        )
        row = cur.fetchone()
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "Tech not found"})

        return {
            "status": "ok",
            "tech": {
                "id": row.get("id"),
                "role": row.get("role") or "",
                "pay_rate": float(row.get("pay_rate") or 0),
            },
        }
    finally:
        cur.close()


@router.post("/techs/delete")
async def delete_tech(request: Request):
    """Soft delete a technician (set active=false)."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    tech_id = data.get("id")

    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "Tech id is required"})

    conn = get_conn()
    cur = conn.cursor()

    try:
        _ensure_techs_table(cur)
        cur.execute(
            """
            UPDATE techs
            SET active = false
                        WHERE id = %s
                            AND (domain = %s OR domain IS NULL)
            RETURNING id
            """,
                        (tech_id, domain),
        )
        row = cur.fetchone()
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "Tech not found"})

        return {"status": "ok", "id": row["id"]}
    finally:
        cur.close()


@router.post("/techs/archive")
async def archive_techs(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    tech_ids = data.get("ids") or []
    normalized_ids = []
    for value in tech_ids:
        try:
            normalized_ids.append(int(value))
        except Exception:
            continue

    if not normalized_ids:
        return JSONResponse(status_code=400, content={"error": "No tech ids provided"})

    conn = get_conn()
    cur = conn.cursor()
    archived = []
    try:
        _ensure_techs_table(cur)
        _ensure_ro_line_assignments_table(cur)
        _ensure_archived_techs_table(cur)

        cur.execute(
            """
            SELECT id, first_name, last_name, pay_rate
            FROM techs
            WHERE id = ANY(%s)
              AND active = TRUE
              AND (domain = %s OR domain IS NULL)
            ORDER BY first_name, last_name
            """,
            (normalized_ids, domain),
        )
        tech_rows = cur.fetchall() or []

        for tech in tech_rows:
            tech_id = int(tech.get("id"))
            tech_name = " ".join(
                part for part in [(tech.get("first_name") or "").strip(), (tech.get("last_name") or "").strip()] if part
            )
            pay_rate = _parse_float_value(tech.get("pay_rate"))

            cur.execute(
                """
                SELECT ro, COALESCE(SUM(hours), 0) AS hours
                FROM ro_line_assignments
                WHERE domain = %s
                  AND tech_id = %s
                  AND tech_name IS NOT NULL
                  AND COALESCE(ready_to_flag, FALSE) = FALSE
                GROUP BY ro
                ORDER BY ro
                """,
                (domain, tech_id),
            )
            ro_rows = cur.fetchall() or []

            assigned_ros = []
            total_hours = 0.0
            for row in ro_rows:
                ro_value = (row.get("ro") or "").strip()
                hours_value = _parse_float_value(row.get("hours"))
                if not ro_value:
                    continue
                assigned_ros.append({"ro": ro_value, "hours": hours_value})
                total_hours += hours_value

            cur.execute(
                """
                INSERT INTO archived_techs (tech_id, tech_name, pay_rate, assigned_ros, total_hours, domain)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    tech_id,
                    tech_name,
                    pay_rate,
                    json.dumps(assigned_ros),
                    total_hours,
                    domain,
                ),
            )

            cur.execute(
                """
                UPDATE techs
                SET active = FALSE
                WHERE id = %s
                """,
                (tech_id,),
            )

            archived.append({
                "tech_id": tech_id,
                "tech_name": tech_name,
                "pay_rate": pay_rate,
                "assigned_ros": assigned_ros,
                "total_hours": total_hours,
            })

        conn.commit()
        return {"status": "ok", "archived": archived}
    finally:
        cur.close()


@router.get("/techs/archived")
async def list_archived_techs(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_archived_techs_table(cur)
        cur.execute(
            """
            SELECT id, tech_id, tech_name, pay_rate, assigned_ros, total_hours, archived_at
            FROM archived_techs
            WHERE domain = %s
            ORDER BY archived_at DESC, id DESC
            """,
            (domain,),
        )
        rows = cur.fetchall() or []
        archived = []
        for row in rows:
            archived.append(
                {
                    "id": row.get("id"),
                    "tech_id": row.get("tech_id"),
                    "tech_name": row.get("tech_name") or "",
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                    "assigned_ros": _parse_json_field(row.get("assigned_ros")),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "archived_at": row.get("archived_at").isoformat() if row.get("archived_at") else None,
                }
            )
        return {"archived": archived}
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
        "ro_assignments",
        "ro_line_assignments",
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
        _ensure_ro_line_assignments_table(cur)
        _ensure_techs_table(cur)

        cur.execute(
            """
            SELECT id, first_name, last_name
            FROM techs
            WHERE active = TRUE
              AND status = 'Active'
              AND (domain = %s OR domain IS NULL)
            """,
            (domain,),
        )
        active_name_set = {
            " ".join(part for part in [(row.get("first_name") or "").strip(), (row.get("last_name") or "").strip()] if part)
            for row in (cur.fetchall() or [])
        }
        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                     id,
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
                                     phone_override,
                                     in_date,
                                     ecd_date,
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
            in_date_value = _coerce_date(row.get("in_date")) or _coerce_date(row.get("saved_at"))
            ecd_date_value = _coerce_date(row.get("ecd_date")) or _calculate_ecd_date(in_date_value, ro_hours)

            _ensure_ro_line_assignments_for_ro(cur, domain, ro)

            cur.execute(
                """
                SELECT repair_type, tech_name, COALESCE(SUM(hours), 0) AS total_hours
                FROM ro_line_assignments
                WHERE domain = %s
                  AND ro = %s
                GROUP BY repair_type, tech_name
                """,
                (domain, ro),
            )
            grouped_lines = cur.fetchall()

            labor_tech = "Unassigned"
            paint_tech = "Unassigned"
            for group in grouped_lines:
                repair_type = _normalize_repair_type(group.get("repair_type"))
                tech_name = (group.get("tech_name") or "").strip()
                if tech_name and tech_name not in active_name_set:
                    tech_name = ""
                if repair_type == "body" and tech_name:
                    labor_tech = tech_name
                if repair_type == "paint" and tech_name:
                    paint_tech = tech_name

            ro_list.append(
                {
                    "ro": ro,
                    "vehicle": vehicle_display,
                    "customer": customer_name,
                    "phone": current_phone,
                    "phone_original": phone_original,
                    "insurance": row.get("insurance_company") or "",
                    "claim_number": row.get("claim_number") or "",
                    "tech": labor_tech,
                    "painter": paint_tech,
                    "in_date": in_date_value.isoformat() if in_date_value else None,
                    "ecd_date": ecd_date_value.isoformat() if ecd_date_value else None,
                    "hours": ro_hours,
                    "total": grand_total,
                    "labor_repairs": labor_repairs if isinstance(labor_repairs, list) else [],
                    "paint_repairs": paint_repairs if isinstance(paint_repairs, list) else [],
                    "parts_repairs": parts_repairs if isinstance(parts_repairs, list) else [],
                }
            )

            ro_seen_for_tech = set()
            for group in grouped_lines:
                tech_name = (group.get("tech_name") or "").strip()
                if tech_name and tech_name not in active_name_set:
                    tech_name = ""
                tech_name = tech_name or "Unassigned"
                group_hours = _parse_float_value(group.get("total_hours"))
                labor_hours_by_tech[tech_name] = labor_hours_by_tech.get(tech_name, 0.0) + group_hours
                if tech_name not in ro_seen_for_tech:
                    ros_by_tech[tech_name] = ros_by_tech.get(tech_name, 0) + 1
                    ro_seen_for_tech.add(tech_name)

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
            "totalROs": ro_count,
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


@router.patch("/ro-dates")
async def update_ro_dates(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    field = (data.get("field") or "").strip().lower()
    value = (data.get("value") or "").strip()

    if not ro_value or field not in {"in_date", "ecd_date"} or not value:
        return JSONResponse(status_code=400, content={"error": "ro, field, and value are required"})

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "value must be YYYY-MM-DD"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        cur.execute(
            """
            SELECT id
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

        if field == "in_date":
            cur.execute(
                """
                UPDATE saved_estimates
                SET in_date = %s
                WHERE id = %s
                """,
                (parsed_date, row.get("id")),
            )
        else:
            cur.execute(
                """
                UPDATE saved_estimates
                SET ecd_date = %s
                WHERE id = %s
                """,
                (parsed_date, row.get("id")),
            )

        conn.commit()
        return {"status": "success", "field": field, "value": parsed_date.isoformat()}
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


@router.get("/ro-tech-lines")
async def get_ro_tech_lines(request: Request, ro: str):
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
        _ensure_ro_line_assignments_table(cur)
        _ensure_techs_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT id
            FROM techs
            WHERE active = TRUE
              AND status = 'Active'
              AND (domain = %s OR domain IS NULL)
            """,
            (domain,),
        )
        active_ids = {int(row.get("id")) for row in (cur.fetchall() or []) if row.get("id") is not None}
        cur.execute(
            """
            SELECT first_name, last_name
            FROM techs
            WHERE active = TRUE
              AND status = 'Active'
              AND (domain = %s OR domain IS NULL)
            """,
            (domain,),
        )
        active_names = {
            " ".join(part for part in [(row.get("first_name") or "").strip(), (row.get("last_name") or "").strip()] if part)
            for row in (cur.fetchall() or [])
        }

        cur.execute(
            """
            SELECT
                repair_type,
                tech_id,
                tech_name,
                COALESCE(is_pending, FALSE) AS is_pending,
                COALESCE(SUM(hours), 0) AS hours,
                COUNT(*) AS line_count
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
            GROUP BY repair_type, tech_id, tech_name, COALESCE(is_pending, FALSE)
            ORDER BY tech_name NULLS FIRST, repair_type
            """,
            (domain, ro_value),
        )
        rows = cur.fetchall()

        tech_lines = []
        pending_hours = 0.0
        pending_count = 0

        for row in rows:
            repair_type = _normalize_repair_type(row.get("repair_type"))
            hours = _parse_float_value(row.get("hours"))
            line_count = int(row.get("line_count") or 0)
            tech_name = (row.get("tech_name") or "").strip()
            tech_id = row.get("tech_id")
            if tech_name and tech_id is not None and int(tech_id) not in active_ids:
                tech_name = ""
            if tech_name and tech_id is None and tech_name not in active_names:
                tech_name = ""
            is_pending = bool(row.get("is_pending"))

            if not tech_name and is_pending:
                pending_hours += hours
                pending_count += line_count
                continue

            if not tech_name:
                tech_lines.append(
                    {
                        "tech": "unassigned",
                        "type": repair_type,
                        "hours": hours,
                        "line_count": line_count,
                        "mode": "unassigned",
                        "repair_type": repair_type,
                    }
                )
                continue

            tech_lines.append(
                {
                    "tech": tech_name,
                    "type": repair_type,
                    "hours": hours,
                    "line_count": line_count,
                    "mode": "tech",
                    "repair_type": repair_type,
                    "tech_id": row.get("tech_id"),
                    "tech_name": tech_name,
                }
            )

        if pending_count > 0:
            tech_lines.append(
                {
                    "tech": "PENDING",
                    "type": "?",
                    "hours": pending_hours,
                    "line_count": pending_count,
                    "mode": "pending",
                }
            )

        def _sort_key(item: dict) -> tuple:
            mode = item.get("mode")
            if mode == "unassigned":
                return (0, item.get("type") or "")
            if mode == "tech":
                return (1, (item.get("tech") or "").lower(), item.get("type") or "")
            if mode == "pending":
                return (2, "")
            return (3, "")

        tech_lines.sort(key=_sort_key)
        return {"tech_lines": tech_lines}
    finally:
        cur.close()


@router.get("/ro-assignment-lines")
async def get_ro_assignment_lines(
    request: Request,
    ro: str,
    mode: str,
    repair_type: str = "",
    tech_name: str = "",
):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    ro_value = (ro or "").strip()
    mode_value = (mode or "").strip().lower()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})
    if mode_value not in {"unassigned", "pending", "tech"}:
        return JSONResponse(status_code=400, content={"error": "mode is invalid"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_line_assignments_table(cur)
        _ensure_techs_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        if mode_value == "unassigned":
            filter_type = _normalize_repair_type(repair_type)
            cur.execute(
                """
                SELECT repair_type, line_key, line_number, description, hours
                FROM ro_line_assignments
                WHERE domain = %s
                  AND ro = %s
                  AND tech_name IS NULL
                  AND COALESCE(is_pending, FALSE) = FALSE
                  AND repair_type = %s
                ORDER BY line_number
                """,
                (domain, ro_value, filter_type),
            )
        elif mode_value == "pending":
            cur.execute(
                """
                SELECT repair_type, line_key, line_number, description, hours
                FROM ro_line_assignments
                WHERE domain = %s
                  AND ro = %s
                  AND tech_name IS NULL
                  AND COALESCE(is_pending, FALSE) = TRUE
                ORDER BY repair_type, line_number
                """,
                (domain, ro_value),
            )
        else:
            filter_type = _normalize_repair_type(repair_type)
            selected_tech = (tech_name or "").strip()
            cur.execute(
                """
                SELECT repair_type, line_key, line_number, description, hours
                FROM ro_line_assignments
                WHERE domain = %s
                  AND ro = %s
                  AND tech_name = %s
                  AND repair_type = %s
                ORDER BY line_number
                """,
                (domain, ro_value, selected_tech, filter_type),
            )

        line_rows = cur.fetchall()

        cur.execute(
            """
            SELECT id, first_name, last_name, pay_rate
            FROM techs
            WHERE active = TRUE
                            AND status = 'Active'
              AND (domain = %s OR domain IS NULL)
            ORDER BY first_name, last_name
            """,
            (domain,),
        )
        tech_rows = cur.fetchall()

        lines = []
        for row in line_rows:
            lines.append(
                {
                    "repair_type": _normalize_repair_type(row.get("repair_type")),
                    "line_key": str(row.get("line_key") or ""),
                    "line_number": row.get("line_number") or "",
                    "description": row.get("description") or "",
                    "hours": _parse_float_value(row.get("hours")),
                }
            )

        techs = []
        for row in tech_rows:
            first_name = (row.get("first_name") or "").strip()
            last_name = (row.get("last_name") or "").strip()
            label = " ".join(part for part in [first_name, last_name] if part)
            techs.append(
                {
                    "id": row.get("id"),
                    "name": label,
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                }
            )

        return {
            "lines": lines,
            "techs": techs,
            "types": ["body", "paint", "mech", "frame"],
        }
    finally:
        cur.close()


@router.post("/ro-assignment-save")
async def save_ro_assignment_lines(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    source = data.get("source") or {}
    target = data.get("target") or {}
    selected_lines = data.get("selected_lines") or []

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    target_tech_id = target.get("tech_id")
    target_tech_name = (target.get("tech_name") or "").strip()
    target_type = _normalize_repair_type(target.get("repair_type"))

    if not target_tech_name and not target_tech_id:
        return JSONResponse(status_code=400, content={"error": "tech is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_line_assignments_table(cur)
        _ensure_techs_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        if target_tech_id:
            cur.execute(
                """
                SELECT id, first_name, last_name
                FROM techs
                WHERE id = %s
                  AND active = TRUE
                                    AND status = 'Active'
                  AND (domain = %s OR domain IS NULL)
                """,
                (target_tech_id, domain),
            )
            tech_row = cur.fetchone()
            if not tech_row:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})
            if not target_tech_name:
                target_tech_name = " ".join(part for part in [tech_row.get("first_name"), tech_row.get("last_name")] if part)

        if not target_tech_id and target_tech_name:
            cur.execute(
                """
                SELECT id
                FROM techs
                WHERE active = TRUE
                                    AND status = 'Active'
                  AND (domain = %s OR domain IS NULL)
                  AND TRIM(CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) = %s
                LIMIT 1
                """,
                (domain, target_tech_name),
            )
            active_named = cur.fetchone()
            if not active_named:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})

        scope_rows = _get_scope_rows(cur, domain, ro_value, source)
        if not scope_rows:
            return {"status": "ok"}

        scope_keys = {
            (str(row.get("repair_type") or ""), str(row.get("line_key") or "")): int(row.get("id"))
            for row in scope_rows
        }

        selected_keys = set()
        for item in selected_lines:
            if not isinstance(item, dict):
                continue
            repair_type = _normalize_repair_type(item.get("repair_type"))
            line_key = str(item.get("line_key") or "")
            selected_keys.add((repair_type, line_key))

        selected_ids = []
        remainder_ids = []
        for key, row_id in scope_keys.items():
            if key in selected_keys:
                selected_ids.append(row_id)
            else:
                remainder_ids.append(row_id)

        if selected_ids:
            cur.execute(
                """
                UPDATE ro_line_assignments
                SET tech_id = %s,
                    tech_name = %s,
                    repair_type = %s,
                    is_pending = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                """,
                (target_tech_id, target_tech_name or None, target_type, selected_ids),
            )

        if remainder_ids:
            cur.execute(
                """
                UPDATE ro_line_assignments
                SET tech_id = NULL,
                    tech_name = NULL,
                    is_pending = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                """,
                (remainder_ids,),
            )

        conn.commit()
        return {"status": "ok"}
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
        _ensure_saved_estimates_table(cur)
        _ensure_ro_assignments_table(cur)
        _ensure_techs_table(cur)

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
        estimate_row = cur.fetchone() or {}
        labor_repairs = _parse_json_field(estimate_row.get("labor_repairs"))
        paint_repairs = _parse_json_field(estimate_row.get("paint_repairs"))
        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []

        lines = labor_repairs if role == "labor" else paint_repairs
        assigned_hours = _sum_assigned_hours(lines, excluded_lines)

        if tech_id:
            cur.execute(
                """
                SELECT id, first_name, last_name
                FROM techs
                WHERE id = %s
                  AND active = TRUE
                                    AND status = 'Active'
                  AND (domain = %s OR domain IS NULL)
                """,
                (tech_id, domain),
            )
            row = cur.fetchone()
            if not row:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})
            if not tech_name:
                tech_name = " ".join(part for part in [row.get("first_name"), row.get("last_name")] if part)

        if not tech_id and tech_name:
            cur.execute(
                """
                SELECT id
                FROM techs
                WHERE active = TRUE
                                    AND status = 'Active'
                  AND (domain = %s OR domain IS NULL)
                  AND TRIM(CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) = %s
                LIMIT 1
                """,
                (domain, tech_name),
            )
            active_named = cur.fetchone()
            if not active_named:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})

        cur.execute(
            """
            INSERT INTO ro_assignments (ro, role, tech_id, tech_name, excluded_lines, assigned_hours, domain)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ro, role, domain)
            DO UPDATE SET
                tech_id = EXCLUDED.tech_id,
                tech_name = EXCLUDED.tech_name,
                excluded_lines = EXCLUDED.excluded_lines,
                assigned_hours = EXCLUDED.assigned_hours,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                ro_value,
                role,
                tech_id,
                tech_name or None,
                json.dumps(excluded_lines),
                assigned_hours,
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
        _ensure_ro_line_assignments_table(cur)
        _ensure_ro_flagout_lines_table(cur)
        _ensure_saved_estimates_table(cur)

        cur.execute(
            """
            WITH latest_estimates AS (
                SELECT DISTINCT ON (ro)
                    ro,
                    year,
                    make,
                    model,
                    vehicle
                FROM saved_estimates
                WHERE domain = %s
                  AND ro IS NOT NULL
                  AND ro <> ''
                ORDER BY ro, saved_at DESC, id DESC
            )
            SELECT
                a.ro,
                COALESCE(SUM(a.hours), 0) AS total_hours,
                le.year,
                le.make,
                le.model,
                le.vehicle
            FROM ro_line_assignments a
            LEFT JOIN latest_estimates le ON le.ro = a.ro
            WHERE a.domain = %s
              AND a.tech_id = %s
              AND a.tech_name IS NOT NULL
              AND a.repair_type = 'body'
              AND COALESCE(a.ready_to_flag, FALSE) = FALSE
            GROUP BY a.ro, le.year, le.make, le.model, le.vehicle
            ORDER BY ro
            """,
            (domain, domain, tech_id),
        )
        assignment_rows = cur.fetchall()

        assignments = []
        for row in assignment_rows:
            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_text = " ".join(part for part in [year, make, model] if part)
            if not vehicle_text:
                vehicle_text = (row.get("vehicle") or "").strip()
            assignments.append(
                {
                    "ro": row.get("ro"),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "vehicle": vehicle_text,
                }
            )

        return {"assignments": assignments}
    finally:
        cur.close()


@router.get("/tech-assignment-lines")
async def get_tech_assignment_lines(request: Request, tech_id: int, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    ro_value = (ro or "").strip()
    if not tech_id or not ro_value:
        return JSONResponse(status_code=400, content={"error": "tech_id and ro are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_line_assignments_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT
                line_key,
                line_number,
                description,
                hours
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_id = %s
              AND repair_type = 'body'
              AND COALESCE(ready_to_flag, FALSE) = FALSE
            ORDER BY line_number
            """,
            (domain, ro_value, tech_id),
        )
        rows = cur.fetchall()

        lines = []
        total_hours = 0.0
        for row in rows:
            hours = _parse_float_value(row.get("hours"))
            total_hours += hours
            lines.append(
                {
                    "line_key": str(row.get("line_key") or ""),
                    "line": row.get("line_number") or "",
                    "description": row.get("description") or "",
                    "value": hours,
                }
            )

        return {
            "lines": lines,
            "total_hours": total_hours,
        }
    finally:
        cur.close()


@router.post("/tech-flag-out")
async def tech_flag_out_lines(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    tech_id = data.get("tech_id")
    selected_line_keys = data.get("line_keys") or []
    pay_rate = _parse_float_value(data.get("pay_rate"))

    if not ro_value or not tech_id:
        return JSONResponse(status_code=400, content={"error": "ro and tech_id are required"})

    normalized_keys = [str(key).strip() for key in selected_line_keys if str(key).strip()]
    if not normalized_keys:
        return JSONResponse(status_code=400, content={"error": "line_keys is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_line_assignments_table(cur)
        _ensure_ro_flagout_lines_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT id, line_key, line_number, description, hours, tech_name, repair_type
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_id = %s
              AND repair_type = 'body'
              AND COALESCE(ready_to_flag, FALSE) = FALSE
              AND line_key = ANY(%s)
            """,
            (domain, ro_value, tech_id, normalized_keys),
        )
        rows = cur.fetchall()

        if not rows:
            return JSONResponse(status_code=404, content={"error": "No matching unpaid labor lines found"})

        row_ids = [int(row.get("id")) for row in rows if row.get("id") is not None]
        flagged_hours = 0.0
        flagged_pay = 0.0
        for row in rows:
            line_hours = _parse_float_value(row.get("hours"))
            line_pay = line_hours * pay_rate
            flagged_hours += line_hours
            flagged_pay += line_pay
            cur.execute(
                """
                INSERT INTO ro_flagout_lines (
                    ro,
                    tech_id,
                    tech_name,
                    repair_type,
                    line_key,
                    line_number,
                    description,
                    hours,
                    pay_rate,
                    pay_amount,
                    status,
                    domain,
                    flagged_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ready_to_flag', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (ro, tech_id, repair_type, line_key, domain)
                DO UPDATE SET
                    line_number = EXCLUDED.line_number,
                    description = EXCLUDED.description,
                    hours = EXCLUDED.hours,
                    pay_rate = EXCLUDED.pay_rate,
                    pay_amount = EXCLUDED.pay_amount,
                    status = 'ready_to_flag',
                    flagged_at = CURRENT_TIMESTAMP
                """,
                (
                    ro_value,
                    tech_id,
                    row.get("tech_name"),
                    row.get("repair_type") or "body",
                    row.get("line_key"),
                    row.get("line_number"),
                    row.get("description"),
                    row.get("hours"),
                    pay_rate,
                    line_pay,
                    domain,
                ),
            )

        if row_ids:
            cur.execute(
                """
                UPDATE ro_line_assignments
                SET ready_to_flag = TRUE,
                    flagged_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                """,
                (row_ids,),
            )

        cur.execute(
            """
            SELECT COUNT(*) AS remaining_count
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_id = %s
              AND repair_type = 'body'
              AND COALESCE(ready_to_flag, FALSE) = FALSE
            """,
            (domain, ro_value, tech_id),
        )
        remaining_row = cur.fetchone() or {}
        remaining_count = int(remaining_row.get("remaining_count") or 0)

        conn.commit()
        return {
            "status": "ok",
            "flagged_count": len(row_ids),
            "flagged_hours": flagged_hours,
            "pay_rate": pay_rate,
            "flagged_pay": flagged_pay,
            "remaining_count": remaining_count,
            "ro_completed": remaining_count == 0,
        }
    finally:
        cur.close()


@router.get("/flagout/techs")
async def get_flagout_techs(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)

        cur.execute(
            """
            SELECT
                f.tech_id,
                COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text)) AS tech_name,
                COALESCE(MAX(f.pay_rate), 0) AS pay_rate,
                COALESCE(SUM(f.hours), 0) AS total_hours,
                COALESCE(SUM(f.pay_amount), 0) AS total_pay
            FROM ro_flagout_lines f
            WHERE f.domain = %s
              AND f.status = 'ready_to_flag'
            GROUP BY f.tech_id
            ORDER BY COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text))
            """,
            (domain,),
        )
        tech_rows = cur.fetchall() or []

        cur.execute(
            """
            WITH latest_estimates AS (
                SELECT DISTINCT ON (ro)
                    ro,
                    year,
                    make,
                    model,
                    vehicle
                FROM saved_estimates
                WHERE domain = %s
                ORDER BY ro, saved_at DESC, id DESC
            )
            SELECT
                f.tech_id,
                f.ro,
                COALESCE(MAX(f.pay_rate), 0) AS pay_rate,
                COALESCE(SUM(f.hours), 0) AS total_hours,
                COUNT(*) AS line_count,
                MAX(f.flagged_at) AS flagged_at,
                MAX(le.year) AS year,
                MAX(le.make) AS make,
                MAX(le.model) AS model,
                MAX(le.vehicle) AS vehicle
            FROM ro_flagout_lines f
            LEFT JOIN latest_estimates le ON le.ro = f.ro
            WHERE f.domain = %s
              AND f.status = 'ready_to_flag'
            GROUP BY f.tech_id, f.ro
            ORDER BY f.tech_id, f.ro
            """,
            (domain, domain),
        )
        ro_rows = cur.fetchall() or []

        ro_map = {}
        for row in ro_rows:
            tech_id = int(row.get("tech_id") or 0)
            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_info = " ".join(part for part in [year, make, model] if part)
            if not vehicle_info:
                vehicle_info = (row.get("vehicle") or "").strip()
            ro_map.setdefault(tech_id, []).append(
                {
                    "ro": row.get("ro") or "",
                    "vehicle_info": vehicle_info,
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "line_count": int(row.get("line_count") or 0),
                    "flagged_at": row.get("flagged_at").isoformat() if row.get("flagged_at") else None,
                }
            )

        techs = []
        for row in tech_rows:
            tech_id = int(row.get("tech_id") or 0)
            techs.append(
                {
                    "tech_id": tech_id,
                    "tech_name": row.get("tech_name") or f"Tech #{tech_id}",
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "total_pay": _parse_float_value(row.get("total_pay")),
                    "ros": ro_map.get(tech_id, []),
                }
            )

        return {"techs": techs}
    finally:
        cur.close()


@router.post("/phase/update")
async def phase_update(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

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

@router.get("/ro-tech-assignments")
async def get_ro_tech_assignments(request: Request, ro: str):
    """Get all tech assignments for a specific RO with total hours and rates."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    if not ro:
        return JSONResponse(status_code=400, content={"error": "RO is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_assignments_table(cur)
        _ensure_techs_table(cur)
        _ensure_saved_estimates_table(cur)

        # Get assignments with tech info
        cur.execute(
            """
            SELECT a.ro, a.role, a.tech_id, a.tech_name, a.excluded_lines, a.assigned_hours,
                   t.hourly_rate as tech_rate
            FROM ro_assignments a
            LEFT JOIN techs t ON a.tech_id = t.id
            WHERE a.domain = %s AND a.ro = %s
            """,
            (domain, ro),
        )
        assignment_rows = cur.fetchall()

        if not assignment_rows:
            return {"assignments": []}

        # Get the estimate data to calculate actual hours
        cur.execute(
            """
            SELECT labor_repairs, paint_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro),
        )
        estimate_row = cur.fetchone()
        
        labor_repairs = _parse_json_field(estimate_row.get("labor_repairs") if estimate_row else None)
        paint_repairs = _parse_json_field(estimate_row.get("paint_repairs") if estimate_row else None)
        
        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []

        assignments = []
        for row in assignment_rows:
            role = row.get("role", "labor")
            lines = labor_repairs if role == "labor" else paint_repairs
            excluded_lines = _parse_json_field(row.get("excluded_lines")) or []
            
            total_hours = _sum_assigned_hours(lines, excluded_lines)
            
            assignments.append({
                "tech_id": row.get("tech_id"),
                "tech_name": row.get("tech_name") or "Unknown",
                "role": role,
                "tech_rate": float(row.get("tech_rate") or 0),
                "total_hours": total_hours,
            })

        return {"assignments": assignments}
    finally:
        cur.close()


@router.get("/ro-tech-detail")
async def get_ro_tech_detail(request: Request, ro: str, tech_id: int, role: str):
    """Get detailed repair lines for a specific tech assignment on an RO."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    if not ro or not tech_id or not role:
        return JSONResponse(status_code=400, content={"error": "RO, tech_id, and role are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_assignments_table(cur)
        _ensure_saved_estimates_table(cur)

        # Get the assignment
        cur.execute(
            """
            SELECT excluded_lines
            FROM ro_assignments
            WHERE domain = %s AND ro = %s AND tech_id = %s AND role = %s
            """,
            (domain, ro, tech_id, role),
        )
        assignment_row = cur.fetchone()
        
        if not assignment_row:
            return {"repair_lines": [], "total_hours": 0}

        excluded_lines = _parse_json_field(assignment_row.get("excluded_lines")) or []

        # Get the estimate data
        cur.execute(
            """
            SELECT labor_repairs, paint_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro),
        )
        estimate_row = cur.fetchone()
        
        if not estimate_row:
            return {"repair_lines": [], "total_hours": 0}

        labor_repairs = _parse_json_field(estimate_row.get("labor_repairs"))
        paint_repairs = _parse_json_field(estimate_row.get("paint_repairs"))
        
        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []

        lines = labor_repairs if role == "labor" else paint_repairs
        
        # Filter out excluded lines
        repair_lines = []
        total_hours = 0
        
        for idx, line in enumerate(lines):
            line_key = str(line.get("line") if line.get("line") is not None else idx + 1)
            if line_key not in excluded_lines:
                repair_lines.append({
                    "line": line.get("line") or line_key,
                    "description": line.get("description") or "",
                    "value": float(line.get("value") or 0),
                })
                total_hours += float(line.get("value") or 0)

        return {
            "repair_lines": repair_lines,
            "total_hours": total_hours
        }
    finally:
        cur.close()


@router.get("/ro-print-data")
async def get_ro_print_data(request: Request, ro: str):
    """Get all data needed for printing RO reports."""
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
        _ensure_ro_notes_table(cur)
        _ensure_ro_line_assignments_table(cur)
        
        # Get estimate data
        cur.execute(
            """
            SELECT 
                ro, vehicle, year, make, model, vin,
                owner_info, insurance_company, claim_number,
                phone_original, phone_override,
                in_date, ecd_date,
                labor_repairs, paint_repairs, parts_repairs,
                parts_total, grand_total, deductible, customer_pay, insurance_pay
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        estimate_row = cur.fetchone()
        
        if not estimate_row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})
        
        # Parse repairs
        labor_repairs = _parse_json_field(estimate_row.get("labor_repairs"))
        paint_repairs = _parse_json_field(estimate_row.get("paint_repairs"))
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs"))
        
        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []
        if not isinstance(parts_repairs, list):
            parts_repairs = []
        
        # Get line assignments to determine which lines belong to which techs/types
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)
        
        cur.execute(
            """
            SELECT repair_type, tech_name, line_key, line_number, description, hours
            FROM ro_line_assignments
            WHERE domain = %s AND ro = %s
            ORDER BY repair_type, line_number
            """,
            (domain, ro_value),
        )
        line_assignments = cur.fetchall()
        
        # Get tech assignments from grouped line assignments (like dashboard does)
        cur.execute(
            """
            SELECT repair_type, tech_name, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE domain = %s AND ro = %s
            GROUP BY repair_type, tech_name
            """,
            (domain, ro_value),
        )
        grouped_lines = cur.fetchall()
        
        tech_assignments = {
            "body": None,
            "paint": None,
            "mech": None
        }
        
        for group in grouped_lines:
            repair_type = _normalize_repair_type(group.get("repair_type", ""))
            tech_name = group.get("tech_name")
            if repair_type == "body" and tech_name:
                tech_assignments["body"] = tech_name
            elif repair_type == "paint" and tech_name:
                tech_assignments["paint"] = tech_name
            elif repair_type in ("mech", "mechanical") and tech_name:
                tech_assignments["mech"] = tech_name
        
        # Organize lines by repair type and tech
        body_lines = []
        paint_lines = []
        mech_lines = []
        
        for line in line_assignments:
            repair_type = _normalize_repair_type(line.get("repair_type", ""))
            line_data = {
                "line": line.get("line_number") or "",
                "description": line.get("description") or "",
                "hours": float(line.get("hours") or 0),
                "tech": line.get("tech_name") or "Unassigned"
            }
            
            if repair_type == "body":
                body_lines.append(line_data)
            elif repair_type == "paint":
                paint_lines.append(line_data)
            elif repair_type in ("mech", "mechanical"):
                mech_lines.append(line_data)
        
        # Get notes
        cur.execute(
            """
            SELECT note, created_at
            FROM ro_notes
            WHERE domain = %s AND ro = %s
            ORDER BY created_at DESC
            """,
            (domain, ro_value),
        )
        note_rows = cur.fetchall()
        notes = [row.get("note") for row in note_rows]
        
        # Parse customer info
        owner_info = estimate_row.get("owner_info") or ""
        customer_name = ""
        if owner_info:
            lines = owner_info.split("\n")
            if lines:
                customer_name = lines[0].strip()
        
        # Format phone
        phone_override = (estimate_row.get("phone_override") or "").strip()
        phone_original = (estimate_row.get("phone_original") or "").strip()
        phone = phone_override or phone_original or ""
        
        # Format vehicle
        year = (estimate_row.get("year") or "").strip()
        make = (estimate_row.get("make") or "").strip()
        model = (estimate_row.get("model") or "").strip()
        vehicle = " ".join(part for part in (year, make, model) if part) or estimate_row.get("vehicle") or ""
        
        # Format dates
        in_date = estimate_row.get("in_date")
        ecd_date = estimate_row.get("ecd_date")
        in_date_str = in_date.isoformat() if in_date else ""
        ecd_date_str = ecd_date.isoformat() if ecd_date else ""
        
        # Calculate totals
        grand_total = float(estimate_row.get("grand_total") or 0)
        insurance_pay = float(estimate_row.get("insurance_pay") or 0)
        customer_pay = float(estimate_row.get("customer_pay") or 0)
        deductible = float(estimate_row.get("deductible") or 0)
        
        # If customer_pay is 0, try to calculate it
        if customer_pay == 0 and deductible > 0:
            customer_pay = deductible
        
        # If insurance_pay is 0, calculate it
        if insurance_pay == 0 and grand_total > 0:
            insurance_pay = grand_total - customer_pay
        
        return {
            "ro": ro_value,
            "vehicle": vehicle,
            "vin": estimate_row.get("vin") or "",
            "customer": customer_name,
            "customer_full": owner_info,
            "phone": phone,
            "insurance": estimate_row.get("insurance_company") or "",
            "claim_number": estimate_row.get("claim_number") or "",
            "in_date": in_date_str,
            "ecd_date": ecd_date_str,
            "techs": tech_assignments,
            "totals": {
                "grand_total": grand_total,
                "insurance_total": insurance_pay,
                "customer_total": customer_pay
            },
            "body_lines": body_lines,
            "paint_lines": paint_lines,
            "mech_lines": mech_lines,
            "notes": notes
        }
    finally:
        cur.close()
