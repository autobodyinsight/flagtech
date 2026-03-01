import json
import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL")

conn = None


def _ensure_sslmode(dsn: str) -> str:
    parsed = urlsplit(dsn)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query:
        query["sslmode"] = "require"
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is required")

    dsn_with_ssl = _ensure_sslmode(DATABASE_URL)
    global conn
    if conn is None or conn.closed:
        conn = psycopg2.connect(dsn_with_ssl, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = True
    return conn


def _parse_float(value) -> float:
    try:
        if value is None:
            return 0.0
        text = str(value).replace("$", "").replace(",", "").strip()
        return float(text) if text else 0.0
    except Exception:
        return 0.0


def _parse_owner_customer(owner_info: str) -> str:
    text = (owner_info or "").strip()
    if not text:
        return ""
    match = re.search(r"customer\s*:\s*([^\n,]+)", text, re.IGNORECASE)
    if match:
        return (match.group(1) or "").strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0] if lines else ""


def _normalize_json_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            import json

            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


def _normalize_json_obj(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _sum_hours(items) -> float:
    total = 0.0
    for item in _normalize_json_list(items):
        if isinstance(item, dict):
            total += _parse_float(item.get("value"))
    return total


def _percent(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def get_closed_ros_and_summary():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ro_phases (
                id SERIAL PRIMARY KEY,
                ro VARCHAR(255) NOT NULL,
                phase VARCHAR(50) NOT NULL,
                domain VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_phases_ro_domain ON ro_phases(ro, domain)")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_estimates (
                id SERIAL PRIMARY KEY,
                ro VARCHAR(255),
                domain VARCHAR(255),
                vehicle TEXT,
                year VARCHAR(10),
                make VARCHAR(80),
                model VARCHAR(80),
                owner_info TEXT,
                insurance_company TEXT,
                estimator TEXT,
                written_by TEXT,
                in_date DATE,
                picked_up DATE,
                labor_repairs JSONB,
                paint_repairs JSONB,
                parts_repairs JSONB,
                estimate_totals JSONB,
                parts_total NUMERIC,
                grand_total NUMERIC,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_totals JSONB")
        cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimator TEXT")
        cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS written_by TEXT")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ro_line_assignments (
                id SERIAL PRIMARY KEY,
                ro VARCHAR(255),
                tech_name VARCHAR(255),
                domain VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS tech_name VARCHAR(255)")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS parts_received (
                id SERIAL PRIMARY KEY,
                ro VARCHAR(255) NOT NULL,
                invoice_number VARCHAR(255),
                invoice_total NUMERIC,
                cost NUMERIC,
                domain VARCHAR(255),
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(255)")
        cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_total NUMERIC")
        cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS cost NUMERIC")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ro_flagout_lines (
                id SERIAL PRIMARY KEY,
                ro VARCHAR(255) NOT NULL,
                pay_amount NUMERIC,
                domain VARCHAR(255),
                flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_amount NUMERIC")

        cur.execute(
            """
            SELECT rp.ro,
                   rp.updated_at AS closed_at,
                   se.vehicle,
                   se.year,
                   se.make,
                   se.model,
                   se.owner_info,
                   se.insurance_company,
                     se.estimator,
                     se.written_by,
                   se.in_date,
                   se.picked_up,
                   se.estimate_totals,
                   se.labor_repairs,
                   se.paint_repairs,
                   se.parts_repairs,
                   se.parts_total,
                   se.grand_total
            FROM ro_phases rp
            LEFT JOIN LATERAL (
                SELECT *
                FROM saved_estimates se
                WHERE se.ro = rp.ro
                ORDER BY se.saved_at DESC, se.id DESC
                LIMIT 1
            ) se ON TRUE
            WHERE COALESCE(LOWER(TRIM(rp.phase)), '') IN ('complete', 'complete/finish')
            ORDER BY rp.updated_at DESC NULLS LAST, rp.ro ASC
            """
        )
        rows = cur.fetchall() or []

        cur.execute(
            """
            SELECT
                invoices.ro,
                COALESCE(SUM(invoices.invoice_paid_total), 0) AS parts_cost
            FROM (
                SELECT
                    ro,
                    invoice_number,
                    COALESCE(NULLIF(SUM(DISTINCT invoice_total), 0), SUM(cost), 0) AS invoice_paid_total
                FROM parts_received
                WHERE ro IS NOT NULL
                  AND ro <> ''
                  AND invoice_number IS NOT NULL
                  AND TRIM(invoice_number) <> ''
                GROUP BY ro, invoice_number

                UNION ALL

                SELECT
                    ro,
                    '__NO_INVOICE__' AS invoice_number,
                    COALESCE(SUM(cost), 0) AS invoice_paid_total
                FROM parts_received
                WHERE ro IS NOT NULL
                  AND ro <> ''
                  AND (invoice_number IS NULL OR TRIM(invoice_number) = '')
                GROUP BY ro
            ) invoices
            GROUP BY invoices.ro
            """
        )
        parts_cost_rows = cur.fetchall() or []
        parts_cost_by_ro = {str(row.get("ro") or "").strip(): _parse_float(row.get("parts_cost")) for row in parts_cost_rows}

        cur.execute(
            """
            SELECT ro, COALESCE(SUM(pay_amount), 0) AS labor_cost
            FROM ro_flagout_lines
            WHERE ro IS NOT NULL
              AND ro <> ''
            GROUP BY ro
            """
        )
        labor_cost_rows = cur.fetchall() or []
        labor_cost_by_ro = {str(row.get("ro") or "").strip(): _parse_float(row.get("labor_cost")) for row in labor_cost_rows}

        cur.execute(
            """
            SELECT ro, STRING_AGG(DISTINCT TRIM(tech_name), ', ' ORDER BY TRIM(tech_name)) AS tech_names
            FROM ro_line_assignments
            WHERE ro IS NOT NULL
              AND ro <> ''
              AND tech_name IS NOT NULL
              AND TRIM(tech_name) <> ''
            GROUP BY ro
            """
        )
        tech_rows = cur.fetchall() or []
        tech_by_ro = {
            str(row.get("ro") or "").strip(): (row.get("tech_names") or "").strip()
            for row in tech_rows
            if str(row.get("ro") or "").strip()
        }

        closed_ros = []
        total_sales = 0.0
        total_parts_sales = 0.0
        total_labor_sales = 0.0
        total_parts_cost = 0.0
        total_labor_cost = 0.0

        for row in rows:
            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")
            customer = _parse_owner_customer((row.get("owner_info") or "").strip())
            insurance = (row.get("insurance_company") or "").strip()
            estimator = (row.get("estimator") or "").strip() or (row.get("written_by") or "").strip()

            labor_repairs = _normalize_json_list(row.get("labor_repairs"))
            paint_repairs = _normalize_json_list(row.get("paint_repairs"))
            parts_repairs = _normalize_json_list(row.get("parts_repairs"))

            hours = _sum_hours(labor_repairs) + _sum_hours(paint_repairs)
            parts_total = _parse_float(row.get("parts_total"))
            if parts_total == 0.0 and parts_repairs:
                parts_total = sum(
                    _parse_float(item.get("price")) * _parse_float(item.get("qty") or 1)
                    for item in parts_repairs
                    if isinstance(item, dict)
                )

            total = _parse_float(row.get("grand_total"))
            estimate_totals = _normalize_json_obj(row.get("estimate_totals"))
            labor_keys = ["body_labor", "paint_labor", "frame_labor", "mechanical_labor", "glass_labor"]
            labor_values = [_parse_float(estimate_totals.get(key)) for key in labor_keys]
            labor_total = sum(labor_values)
            if labor_total <= 0.0:
                labor_total = max(total - parts_total, 0.0)

            total_sales += total
            total_parts_sales += parts_total
            total_labor_sales += labor_total

            ro_key = str(row.get("ro") or "").strip()
            tech_name = tech_by_ro.get(ro_key, "")
            total_parts_cost += parts_cost_by_ro.get(ro_key, 0.0)
            total_labor_cost += labor_cost_by_ro.get(ro_key, 0.0)

            in_date = row.get("in_date")
            picked_up = row.get("picked_up")
            closed_at = row.get("closed_at")
            in_date_text = in_date.isoformat() if hasattr(in_date, "isoformat") else (str(in_date) if in_date else "")
            picked_up_text = picked_up.isoformat() if hasattr(picked_up, "isoformat") else (str(picked_up) if picked_up else "")
            if not picked_up_text:
                picked_up_text = closed_at.date().isoformat() if hasattr(closed_at, "date") else (str(closed_at)[:10] if closed_at else "")

            closed_ros.append(
                {
                    "ro_number": str(row.get("ro") or ""),
                    "vehicle": vehicle,
                    "tech": tech_name,
                    "estimator": estimator,
                    "parts": "",
                    "insurance": insurance,
                    "customer": customer,
                    "in_date": in_date_text,
                    "picked_up": picked_up_text,
                    "hours": hours,
                    "parts_sales": parts_total,
                    "parts_cost": parts_cost_by_ro.get(ro_key, 0.0),
                    "labor_sales": labor_total,
                    "labor_cost": labor_cost_by_ro.get(ro_key, 0.0),
                    "total_sales": total,
                    "total_cost": parts_cost_by_ro.get(ro_key, 0.0) + labor_cost_by_ro.get(ro_key, 0.0),
                    "total": total,
                    "status": "closed",
                    "gp_percent": 0,
                    "gp_dollar": 0,
                    "type": "ro",
                }
            )

        ro_gp_dollar = total_sales - total_parts_cost - total_labor_cost
        parts_gp_dollar = total_parts_sales - total_parts_cost
        labor_gp_dollar = total_labor_sales - total_labor_cost

        summary = {
            "RO'S": {
                "sales": total_sales,
                "gp_percent": _percent(ro_gp_dollar, total_sales),
                "gp_dollar": ro_gp_dollar,
            },
            "PARTS": {
                "sales": total_parts_sales,
                "gp_percent": _percent(parts_gp_dollar, total_parts_sales),
                "gp_dollar": parts_gp_dollar,
            },
            "LABOR": {
                "sales": total_labor_sales,
                "gp_percent": _percent(labor_gp_dollar, total_labor_sales),
                "gp_dollar": labor_gp_dollar,
            },
        }
        return closed_ros, summary
    finally:
        cur.close()


def close_repair_order(ro_number):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE repair_orders
            SET status = 'closed'
            WHERE ro_number = %s
            """,
            (ro_number,),
        )
    finally:
        cur.close()
