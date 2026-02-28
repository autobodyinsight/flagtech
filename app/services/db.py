import json
import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg2
import psycopg2.extras

from app.services.middleware import DEFAULT_SCOPE_DOMAIN

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


def _parse_hours(labor_repairs, paint_repairs) -> float:
    def _sum_hours(items):
        total = 0.0
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    total += _parse_float(item.get("value"))
        return total

    return _sum_hours(labor_repairs) + _sum_hours(paint_repairs)


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
                in_date DATE,
                labor_repairs JSONB,
                paint_repairs JSONB,
                grand_total NUMERIC(12, 2),
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        domain = DEFAULT_SCOPE_DOMAIN
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
                   se.in_date,
                   se.labor_repairs,
                   se.paint_repairs,
                   se.grand_total
            FROM ro_phases rp
            LEFT JOIN LATERAL (
                SELECT *
                FROM saved_estimates se
                WHERE se.ro = rp.ro
                  AND (se.domain = rp.domain OR (se.domain IS NULL AND rp.domain IS NULL))
                ORDER BY se.saved_at DESC, se.id DESC
                LIMIT 1
            ) se ON TRUE
            WHERE COALESCE(LOWER(TRIM(rp.phase)), '') IN ('complete', 'complete/finish')
              AND (rp.domain = %s OR (%s IS NULL AND rp.domain IS NULL))
            ORDER BY rp.updated_at DESC NULLS LAST, rp.ro ASC
            """,
            (domain, domain),
        )
        rows = cur.fetchall() or []

        closed_ros = []
        total_sales = 0.0

        for row in rows:
            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")

            owner_info = (row.get("owner_info") or "").strip()
            customer = _parse_owner_customer(owner_info)
            insurance = (row.get("insurance_company") or "").strip()

            labor_repairs = row.get("labor_repairs")
            if isinstance(labor_repairs, str):
                try:
                    labor_repairs = json.loads(labor_repairs)
                except Exception:
                    labor_repairs = []

            paint_repairs = row.get("paint_repairs")
            if isinstance(paint_repairs, str):
                try:
                    paint_repairs = json.loads(paint_repairs)
                except Exception:
                    paint_repairs = []

            hours = _parse_hours(labor_repairs, paint_repairs)
            total = _parse_float(row.get("grand_total"))
            total_sales += total

            in_date = row.get("in_date")
            closed_at = row.get("closed_at")
            in_date_text = in_date.isoformat() if hasattr(in_date, "isoformat") else (str(in_date) if in_date else "")
            picked_up_text = closed_at.date().isoformat() if hasattr(closed_at, "date") else (str(closed_at)[:10] if closed_at else "")

            closed_ros.append(
                {
                    "ro_number": str(row.get("ro") or ""),
                    "vehicle": vehicle,
                    "tech": "",
                    "parts": "",
                    "insurance": insurance,
                    "customer": customer,
                    "in_date": in_date_text,
                    "picked_up": picked_up_text,
                    "hours": hours,
                    "total": total,
                    "status": "closed",
                    "gp_percent": 0,
                    "gp_dollar": 0,
                    "type": "ro",
                }
            )

        summary = {
            "RO'S": {"sales": total_sales, "gp_percent": 0, "gp_dollar": 0},
            "PARTS": {"sales": 0, "gp_percent": 0, "gp_dollar": 0},
            "LABOR": {"sales": 0, "gp_percent": 0, "gp_dollar": 0},
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
