from fastapi import APIRouter, UploadFile, File, Request
import os
import json
import math
import re
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn
from app.services.middleware import get_user_domain
from fastapi.responses import JSONResponse
from psycopg2 import sql

router = APIRouter()


def _to_local_business_date(value) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not isinstance(value, datetime):
        return None
    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(local_tz).date()


def _normalize_line_ids(values) -> set[int]:
    ids = set()
    if not isinstance(values, list):
        return ids
    for value in values:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        ids.add(parsed)
    return ids


_TRAILING_PART_NUMBER_RE = re.compile(r"\b([A-Z0-9-]{6,})\s*$", re.IGNORECASE)


def _alpha_only_description(value: str) -> str:
    tokens = re.split(r"\s+", str(value or "").strip())
    kept = []
    for token in tokens:
        cleaned = (token or "").strip().strip(",;:|()[]{}")
        if not cleaned:
            continue
        if any(ch.isdigit() for ch in cleaned):
            continue
        letters_only = re.sub(r"[^A-Za-z]", "", cleaned)
        if letters_only:
            kept.append(letters_only)
    return " ".join(kept)


def _serialize_datetime_for_client(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return value


def _resolve_note_created_by(cur, value: str) -> str:
    created_by = str(value or "").strip()
    if not created_by:
        return "Unknown"

    if "@" in created_by:
        try:
            cur.execute(
                """
                SELECT first_name, last_name
                FROM users
                WHERE lower(email) = lower(%s)
                LIMIT 1
                """,
                (created_by,),
            )
            user_row = cur.fetchone() or {}
            first_name = str(user_row.get("first_name") or "").strip()
            last_name = str(user_row.get("last_name") or "").strip()
            full_name = " ".join(part for part in (first_name, last_name) if part)
            if full_name:
                return full_name
        except Exception:
            pass
    return created_by


def _extract_line_number(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except Exception:
            return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    try:
        return int(match.group(0))
    except Exception:
        return None


def _coerce_number(value, default: float = 0.0) -> float:
    try:
        parsed = float(str(value).replace(",", "").strip())
        if math.isfinite(parsed):
            return parsed
    except Exception:
        pass
    return default


def _build_unified_estimate_lines(snapshot: dict | None) -> list[dict]:
    if not isinstance(snapshot, dict):
        return []

    sections = snapshot.get("sections")
    if not isinstance(sections, list):
        sections = []

    by_line: dict[int, dict] = {}
    order: list[int] = []

    def _get_or_create(line_number: int) -> dict:
        if line_number not in by_line:
            by_line[line_number] = {
                "lineNumber": line_number,
                "description": "",
                "labor": 0.0,
                "paint": 0.0,
                "qty": None,
                "partNumber": "",
                "extendedPrice": None,
            }
            order.append(line_number)
        return by_line[line_number]

    seed_lines = snapshot.get("all_lines")
    if isinstance(seed_lines, list):
        for seed in seed_lines:
            if not isinstance(seed, dict):
                continue
            line_number = _extract_line_number(seed.get("line") or seed.get("lineNumber"))
            if line_number is None:
                continue
            record = _get_or_create(line_number)
            seed_description = str(seed.get("description") or "").strip()
            if seed_description and not record.get("description"):
                record["description"] = seed_description

    for section in sections:
        if not isinstance(section, dict):
            continue
        key = str(section.get("key") or "").strip().lower()
        items = section.get("items")
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            line_number = _extract_line_number(item.get("line") or item.get("lineNumber"))
            if line_number is None:
                continue

            record = _get_or_create(line_number)
            item_description = str(item.get("description") or "").strip()
            if item_description and not record.get("description"):
                record["description"] = item_description

            if key == "labor":
                record["labor"] = _coerce_number(item.get("value"), 0.0)
                continue

            if key == "paint":
                record["paint"] = _coerce_number(item.get("value"), 0.0)
                continue

            if key == "parts":
                qty_value = item.get("qty")
                if qty_value is not None and str(qty_value).strip() != "":
                    record["qty"] = _coerce_number(qty_value, 0.0)

                part_number = (
                    item.get("partNumber")
                    or item.get("part_number")
                    or item.get("part_no")
                    or item.get("part#")
                    or item.get("pn")
                    or ""
                )
                part_number = str(part_number or "").strip()
                if part_number:
                    record["partNumber"] = part_number

                price_value = item.get("extendedPrice")
                if price_value is None:
                    price_value = item.get("price")
                if price_value is not None and str(price_value).strip() != "":
                    record["extendedPrice"] = _coerce_number(price_value, 0.0)

    return [by_line[line_number] for line_number in sorted(order)]


def _merge_unified_lines(primary_lines: list[dict] | None, fallback_lines: list[dict] | None) -> list[dict]:
    merged: dict[int, dict] = {}

    def _add_lines(lines: list[dict] | None, prefer_existing: bool) -> None:
        if not isinstance(lines, list):
            return
        for item in lines:
            if not isinstance(item, dict):
                continue
            line_number = _extract_line_number(item.get("lineNumber") or item.get("line"))
            if line_number is None:
                continue
            existing = merged.get(line_number)
            if existing is None:
                merged[line_number] = {
                    "lineNumber": line_number,
                    "description": str(item.get("description") or "").strip(),
                    "labor": _coerce_number(item.get("labor"), 0.0),
                    "paint": _coerce_number(item.get("paint"), 0.0),
                    "qty": item.get("qty"),
                    "partNumber": str(item.get("partNumber") or item.get("part_number") or "").strip(),
                    "extendedPrice": item.get("extendedPrice") if item.get("extendedPrice") is not None else item.get("price"),
                }
                continue

            candidate_description = str(item.get("description") or "").strip()
            if candidate_description and (not existing.get("description") or not prefer_existing):
                existing["description"] = candidate_description

            candidate_labor = item.get("labor")
            if candidate_labor is not None and (existing.get("labor") in (None, 0, 0.0) or not prefer_existing):
                existing["labor"] = _coerce_number(candidate_labor, 0.0)

            candidate_paint = item.get("paint")
            if candidate_paint is not None and (existing.get("paint") in (None, 0, 0.0) or not prefer_existing):
                existing["paint"] = _coerce_number(candidate_paint, 0.0)

            candidate_qty = item.get("qty")
            if candidate_qty is not None and (existing.get("qty") is None or not prefer_existing):
                existing["qty"] = candidate_qty

            candidate_part = str(item.get("partNumber") or item.get("part_number") or "").strip()
            if candidate_part and (not existing.get("partNumber") or not prefer_existing):
                existing["partNumber"] = candidate_part

            candidate_price = item.get("extendedPrice") if item.get("extendedPrice") is not None else item.get("price")
            if candidate_price is not None and (existing.get("extendedPrice") is None or not prefer_existing):
                existing["extendedPrice"] = candidate_price

    _add_lines(fallback_lines, prefer_existing=False)
    _add_lines(primary_lines, prefer_existing=True)

    return [merged[line_number] for line_number in sorted(merged.keys())]


def _parse_part_description_and_number(item: dict) -> tuple[str, str]:
    description = str(item.get("description") or "").strip()
    explicit_part_number = (
        item.get("part_number")
        or item.get("part_no")
        or item.get("part#")
        or item.get("pn")
        or ""
    )
    part_number = str(explicit_part_number or "").strip()

    def _clean_token(token: str) -> str:
        return (token or "").strip().strip(",;:|()[]{}")

    def _is_noise_token(token: str) -> bool:
        cleaned = _clean_token(token)
        if not cleaned:
            return True
        if re.fullmatch(r"\$?\d+(?:\.\d+)?", cleaned):
            return True
        if re.fullmatch(r"\d+(?:\.\d+)?(?:HRS?|HR)?", cleaned, re.IGNORECASE):
            return True
        if cleaned.lower() in {"qty", "incl", "incl.", "list", "price", "labor", "hrs", "hr", "ea", "each"}:
            return True
        return False

    def _is_part_number_token(token: str) -> bool:
        cleaned = _clean_token(token)
        if not re.fullmatch(r"[A-Z0-9-]{5,}", cleaned, re.IGNORECASE):
            return False
        has_alpha = any(ch.isalpha() for ch in cleaned)
        has_digit = any(ch.isdigit() for ch in cleaned)
        return has_alpha and has_digit

    tokens = description.split()
    kept_tokens = []
    for token in tokens:
        if _is_noise_token(token):
            continue
        if _is_part_number_token(token):
            if not part_number:
                part_number = _clean_token(token)
            continue
        kept_tokens.append(token)

    description = " ".join(kept_tokens).strip()

    if not part_number:
        trailing_match = _TRAILING_PART_NUMBER_RE.search(description)
        if trailing_match:
            candidate = _clean_token(trailing_match.group(1) or "")
            has_alpha = any(ch.isalpha() for ch in candidate)
            has_digit = any(ch.isdigit() for ch in candidate)
            if has_alpha and has_digit:
                part_number = candidate
                description = description[:trailing_match.start()].strip()

    description = re.sub(r"\s{2,}", " ", description).strip(" -|,;:")
    description = _alpha_only_description(description)
    return description, part_number


def _ensure_parts_vendors_table(cur) -> None:
    """Create parts_vendors table if it doesn't exist (safety for older DBs)."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_vendors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            vendor_type VARCHAR(100),
            contact_person VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(50),
            street VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            zip VARCHAR(20),
            domain VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS vendor_type VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS street VARCHAR(255)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS city VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS state VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS zip VARCHAR(20)")
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
            estimate_snapshot JSONB,
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
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_snapshot JSONB")
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
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS written_by TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimator TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS vin VARCHAR(32)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS ecd_date DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_ro_domain ON saved_estimates(ro, domain)")


def _ensure_ro_payment_totals_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_payment_totals (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            insurance_paid NUMERIC DEFAULT 0,
            customer_paid NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain, ro)
        )
        """
    )
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS insurance_paid NUMERIC DEFAULT 0")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS customer_paid NUMERIC DEFAULT 0")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_totals_domain_ro ON ro_payment_totals(domain, ro)")


def _ensure_ro_payment_entries_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_payment_entries (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            payer_type VARCHAR(32) NOT NULL,
            amount NUMERIC NOT NULL,
            business_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS ro VARCHAR(255)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS payer_type VARCHAR(32)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS amount NUMERIC")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS business_date DATE")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_entries_domain_ro ON ro_payment_entries(domain, ro)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_entries_domain_ro_type ON ro_payment_entries(domain, ro, payer_type)")


def _ensure_closed_ro_archive_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS closed_ro_archive (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            archived_payload JSONB NOT NULL,
            closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE closed_ro_archive ADD COLUMN IF NOT EXISTS archived_payload JSONB")
    cur.execute("ALTER TABLE closed_ro_archive ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closed_ro_archive_domain_ro ON closed_ro_archive(domain, ro)")


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
            part_number VARCHAR(255),
            qty_received NUMERIC,
            list_price NUMERIC,
            cost NUMERIC,
            eta DATE,
            invoice_number VARCHAR(255),
            invoice_total NUMERIC,
            returned BOOLEAN DEFAULT FALSE,
            returned_at TIMESTAMP,
            received_business_date DATE,
            returned_business_date DATE,
            domain VARCHAR(255) NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS part_number VARCHAR(255)")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS qty_received NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS list_price NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS eta DATE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(255)")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_total NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned_at TIMESTAMP")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS received_business_date DATE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned_business_date DATE")
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
    cur.execute("ALTER TABLE ro_notes ADD COLUMN IF NOT EXISTS created_by VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_notes_ro_domain ON ro_notes(ro, domain)")


def _ensure_ro_activity_log_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_activity_log (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            activity_type VARCHAR(64) NOT NULL,
            message TEXT NOT NULL,
            occurred_on DATE NOT NULL DEFAULT CURRENT_DATE,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_activity_ro_domain ON ro_activity_log(ro, domain, created_at DESC)")


def _activity_to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.utcnow()


def _to_archive_json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _to_archive_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_archive_json_value(item) for item in value]
    return value


def _log_ro_activity(cur, domain: str, ro: str, activity_type: str, message: str, occurred_at=None) -> None:
    if not domain or not ro or not message:
        return
    occurred_dt = _activity_to_datetime(occurred_at)
    cur.execute(
        """
        INSERT INTO ro_activity_log (ro, activity_type, message, occurred_on, domain, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (ro, activity_type, message, occurred_dt.date(), domain, occurred_dt),
    )


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
            flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_rate NUMERIC")
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_amount NUMERIC")
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP")
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
    if re.fullmatch(r"\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}(?:\s*(?:cell|work|home|mobile))?", name, re.IGNORECASE):
        name = ""
    phone = lines[1] if len(lines) > 1 else ""
    if not phone and len(lines) > 0 and re.search(r"\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}", lines[0]):
        phone = lines[0]
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
    role_value = (data.get("role") or "").strip()
    allowed_roles = {"Body", "Frame", "Mech", "Paint"}
    if role_value and role_value not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "role must be Body, Frame, Mech, or Paint"})
    conn = get_conn()
    cur = conn.cursor()

    try:
        _ensure_techs_table(cur)
        cur.execute("""
            INSERT INTO techs (first_name, last_name, pay_rate, domain, status, role, total_ros)
            VALUES (%s, %s, %s, %s, 'Active', %s, 0)
            RETURNING id, first_name, last_name, pay_rate, active, status, role, total_ros
        """, (
            data["first_name"],
            data["last_name"],
            data["pay_rate"],
            domain,
            role_value or "",
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
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()

    allowed_roles = {"Body", "Frame", "Paint", "Mech"}
    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "id is required"})
    if role_value and role_value not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "role must be Body, Frame, Paint, or Mech"})

    pay_rate_value = None
    if pay_rate_raw is not None:
        try:
            pay_rate_value = float(pay_rate_raw)
        except Exception:
            return JSONResponse(status_code=400, content={"error": "pay_rate must be numeric"})

        if pay_rate_value <= 0:
            return JSONResponse(status_code=400, content={"error": "pay_rate must be greater than zero"})

    if (first_name and not last_name) or (last_name and not first_name):
        return JSONResponse(status_code=400, content={"error": "first_name and last_name must both be provided"})

    update_fields = []
    params = []
    if role_value:
        update_fields.append("role = %s")
        params.append(role_value)
    if pay_rate_value is not None:
        update_fields.append("pay_rate = %s")
        params.append(pay_rate_value)
    if first_name and last_name:
        update_fields.append("first_name = %s")
        update_fields.append("last_name = %s")
        params.extend([first_name, last_name])

    if not update_fields:
        return JSONResponse(status_code=400, content={"error": "No valid fields to update"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_techs_table(cur)
        cur.execute(
            f"""
            UPDATE techs
            SET {', '.join(update_fields)}
            WHERE id = %s
              AND active = TRUE
              AND (domain = %s OR domain IS NULL)
            RETURNING id, first_name, last_name, role, pay_rate
            """,
            params + [tech_id, domain],
        )
        row = cur.fetchone()
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "Tech not found"})

        return {
            "status": "ok",
            "tech": {
                "id": row.get("id"),
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
                "role": row.get("role") or "",
                "pay_rate": _parse_float_value(row.get("pay_rate")),
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
    vendor_type = (data.get("vendor_type") or "").strip()
    contact_person = (data.get("contact_person") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    street = (data.get("street") or "").strip()
    city = (data.get("city") or "").strip()
    state = (data.get("state") or "").strip()
    zip_code = (data.get("zip") or "").strip()

    if not name:
        return JSONResponse(status_code=400, content={"error": "Vendor name is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        cur.execute(
            """
            INSERT INTO parts_vendors (name, vendor_type, contact_person, email, phone, street, city, state, zip, domain)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, vendor_type, contact_person, email, phone, street, city, state, zip, active
            """,
            (
                name,
                vendor_type or None,
                contact_person or None,
                email or None,
                phone or None,
                street or None,
                city or None,
                state or None,
                zip_code or None,
                domain,
            ),
        )

        row = cur.fetchone()
        conn.commit()

        return {
            "vendor": {
                "id": row["id"],
                "name": row["name"],
                "vendor_type": row["vendor_type"],
                "contact_person": row["contact_person"],
                "email": row["email"],
                "phone": row["phone"],
                "street": row["street"],
                "city": row["city"],
                "state": row["state"],
                "zip": row["zip"],
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
            SELECT id, name, vendor_type, contact_person, email, phone, street, city, state, zip, active
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
                "vendor_type": row["vendor_type"],
                "contact_person": row["contact_person"],
                "email": row["email"],
                "phone": row["phone"],
                "street": row["street"],
                "city": row["city"],
                "state": row["state"],
                "zip": row["zip"],
                "active": row["active"],
            }
            for row in rows
        ]

        return {"vendors": vendors}
    finally:
        cur.close()


@router.post("/vendors/update")
async def update_vendor(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    vendor_id = data.get("vendor_id")
    try:
        vendor_id = int(vendor_id)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "vendor_id is required"})

    name = (data.get("name") or "").strip()
    vendor_type = (data.get("vendor_type") or "").strip()
    contact_person = (data.get("contact_person") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    street = (data.get("street") or "").strip()
    city = (data.get("city") or "").strip()
    state = (data.get("state") or "").strip()
    zip_code = (data.get("zip") or "").strip()

    if not name:
        return JSONResponse(status_code=400, content={"error": "Vendor name is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        cur.execute(
            """
            UPDATE parts_vendors
            SET
                name = %s,
                vendor_type = %s,
                contact_person = %s,
                phone = %s,
                email = %s,
                street = %s,
                city = %s,
                state = %s,
                zip = %s
            WHERE id = %s AND domain = %s AND active = TRUE
            RETURNING id, name, vendor_type, contact_person, phone, email, street, city, state, zip, active
            """,
            (
                name,
                vendor_type or None,
                contact_person or None,
                phone or None,
                email or None,
                street or None,
                city or None,
                state or None,
                zip_code or None,
                vendor_id,
                domain,
            ),
        )
        row = cur.fetchone()
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "Vendor not found"})

        return {
            "vendor": {
                "id": row["id"],
                "name": row["name"],
                "vendor_type": row["vendor_type"],
                "contact_person": row["contact_person"],
                "phone": row["phone"],
                "email": row["email"],
                "street": row["street"],
                "city": row["city"],
                "state": row["state"],
                "zip": row["zip"],
                "active": row["active"],
            }
        }
    finally:
        cur.close()


@router.post("/flash")
async def flash_data():
    """Delete all row data from public tables while preserving table structure."""
    conn = get_conn()
    cur = conn.cursor()

    deleted_counts = {}
    try:
        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        table_rows = cur.fetchall() or []

        for table_row in table_rows:
            table_schema = table_row.get("table_schema")
            table_name = table_row.get("table_name")
            if not table_schema or not table_name:
                continue
            delete_stmt = sql.SQL("DELETE FROM {}.{}").format(
                sql.Identifier(table_schema),
                sql.Identifier(table_name),
            )
            cur.execute(delete_stmt)
            deleted_counts[f"{table_schema}.{table_name}"] = cur.rowcount

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
        _ensure_ro_phases_table(cur)
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
                                     written_by,
                                     estimator,
                   labor_repairs,
                   paint_repairs,
                   parts_repairs,
                   parts_total,
                   grand_total,
                   owner_info,
                   insurance_company,
                   claim_number,
                   vin,
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
            written_by = (row.get("written_by") or "").strip()
            estimator = (row.get("estimator") or "").strip()
            if not written_by:
                written_match = re.search(r"written\s*by\s*:\s*([^\n,]+)", owner_info, re.IGNORECASE)
                if written_match:
                    written_by = (written_match.group(1) or "").strip()
            if not estimator:
                estimator_match = re.search(r"estimator\s*:\s*([^\n,]+)", owner_info, re.IGNORECASE)
                if estimator_match:
                    estimator = (estimator_match.group(1) or "").strip()
            phone_override = (row.get("phone_override") or "").strip()
            phone_original = (row.get("phone_original") or customer_phone).strip()
            current_phone = phone_override or customer_phone
            in_date_value = _coerce_date(row.get("in_date")) or _to_local_business_date(row.get("saved_at"))
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
                    "owner_info": owner_info,
                    "written_by": written_by,
                    "estimator": estimator,
                    "insurance": row.get("insurance_company") or "",
                    "claim_number": row.get("claim_number") or "",
                    "vin": row.get("vin") or "",
                    "phase": phase_map.get(ro, "teardown"),
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


@router.get("/payments/open-ros")
async def list_open_ros_for_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_phases_table(cur)
        _ensure_ro_payment_totals_table(cur)
        _ensure_ro_payment_entries_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                   year,
                   make,
                   model,
                   owner_info,
                     insurance_company,
                   grand_total,
                   customer_pay,
                   insurance_pay,
                   deductible,
                   saved_at
            FROM saved_estimates
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
            """,
            (domain,),
        )
        rows = cur.fetchall() or []

        cur.execute(
            """
            SELECT ro, phase
            FROM ro_phases
            WHERE domain = %s
            """,
            (domain,),
        )
        phase_rows = cur.fetchall() or []
        phase_map = {str(row.get("ro") or ""): str(row.get("phase") or "").strip().lower() for row in phase_rows}

        cur.execute(
            """
            SELECT ro, insurance_paid, customer_paid
            FROM ro_payment_totals
            WHERE domain = %s
            """,
            (domain,),
        )
        payment_rows = cur.fetchall() or []
        payment_map = {
            str(payment_row.get("ro") or "").strip(): {
                "insurance_paid": _parse_float_value(payment_row.get("insurance_paid")),
                "customer_paid": _parse_float_value(payment_row.get("customer_paid")),
            }
            for payment_row in payment_rows
            if str(payment_row.get("ro") or "").strip()
        }

        cur.execute(
            """
            SELECT ro, payer_type, amount, business_date
            FROM ro_payment_entries
            WHERE domain = %s
            ORDER BY business_date DESC NULLS LAST, id DESC
            """,
            (domain,),
        )
        payment_entry_rows = cur.fetchall() or []
        payment_entries_by_ro = {}
        for entry_row in payment_entry_rows:
            ro_key = str(entry_row.get("ro") or "").strip()
            payer_type = str(entry_row.get("payer_type") or "").strip().lower()
            if not ro_key or payer_type not in {"insurance", "customer"}:
                continue

            business_date = entry_row.get("business_date")
            if isinstance(business_date, datetime):
                business_date_display = business_date.date().isoformat()
            elif isinstance(business_date, date):
                business_date_display = business_date.isoformat()
            else:
                business_date_display = str(business_date or "")[:10]

            entry_bucket = payment_entries_by_ro.setdefault(ro_key, {"insurance": [], "customer": []})
            entry_bucket[payer_type].append(
                {
                    "amount": _parse_float_value(entry_row.get("amount")),
                    "business_date": business_date_display,
                }
            )

        cur.execute(
            """
            SELECT
                ro,
                invoice_number,
                COALESCE(NULLIF(SUM(DISTINCT invoice_total), 0), SUM(cost), 0) AS invoice_paid_total,
                MAX(COALESCE(received_business_date, received_at::date)) AS latest_received_date
            FROM parts_received
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
              AND invoice_number IS NOT NULL
              AND TRIM(invoice_number) <> ''
            GROUP BY ro, invoice_number
            ORDER BY ro, latest_received_date DESC, invoice_number
            """,
            (domain,),
        )
        invoice_rows = cur.fetchall() or []

        invoices_by_ro = {}
        for invoice_row in invoice_rows:
            ro_key = str(invoice_row.get("ro") or "").strip()
            invoice_number = str(invoice_row.get("invoice_number") or "").strip()
            if not ro_key or not invoice_number:
                continue
            invoices_by_ro.setdefault(ro_key, []).append(
                {
                    "invoice_number": invoice_number,
                    "amount_paid": _parse_float_value(invoice_row.get("invoice_paid_total")),
                }
            )

        payments_rows = []
        closed_phase_keys = {"complete", "complete/finish"}

        for row in rows:
            ro = str(row.get("ro") or "").strip()
            if not ro:
                continue

            phase_value = phase_map.get(ro, "teardown")
            if phase_value in closed_phase_keys:
                continue

            customer_name, _ = _parse_owner_info((row.get("owner_info") or "").strip())

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_display = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")

            grand_total = _parse_float_value(row.get("grand_total"))
            customer_total = _parse_float_value(row.get("customer_pay"))
            insurance_total = _parse_float_value(row.get("insurance_pay"))
            deductible = _parse_float_value(row.get("deductible"))

            if customer_total == 0 and deductible > 0:
                customer_total = deductible
            if insurance_total == 0 and grand_total > 0:
                insurance_total = max(0.0, grand_total - customer_total)

            paid_values = payment_map.get(ro) or {}
            insurance_paid = _parse_float_value(paid_values.get("insurance_paid"))
            customer_paid = _parse_float_value(paid_values.get("customer_paid"))
            balance = max(0.0, grand_total - insurance_paid - customer_paid)

            payments_rows.append(
                {
                    "ro": ro,
                    "customer": customer_name,
                    "insurance_name": (row.get("insurance_company") or "").strip(),
                    "vehicle": vehicle_display,
                    "insurance_total": insurance_total,
                    "customer_total": customer_total,
                    "insurance_paid": insurance_paid,
                    "customer_paid": customer_paid,
                    "grand_total": grand_total,
                    "balance": balance,
                    "invoice_payments": invoices_by_ro.get(ro, []),
                    "insurance_payment_entries": (payment_entries_by_ro.get(ro) or {}).get("insurance", []),
                    "customer_payment_entries": (payment_entries_by_ro.get(ro) or {}).get("customer", []),
                }
            )

        payments_rows.sort(key=lambda item: str(item.get("ro") or ""))
        return {"rows": payments_rows}
    finally:
        cur.close()


@router.post("/payments/save")
async def save_ro_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = str(data.get("ro") or "").strip()

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    insurance_paid_raw = data.get("insurance_paid", 0)
    customer_paid_raw = data.get("customer_paid", 0)
    insurance_payment_raw = data.get("insurance_payment", None)
    customer_payment_raw = data.get("customer_payment", None)
    business_date_raw = str(data.get("business_date") or "").strip()
    has_incremental_values = insurance_payment_raw is not None or customer_payment_raw is not None

    def _parse_payment_amount(raw_value) -> float:
        cleaned = str(raw_value if raw_value is not None else "").replace("$", "").replace(",", "").strip()
        if cleaned == "":
            return 0.0
        parsed = float(cleaned)
        if not math.isfinite(parsed):
            raise ValueError("amount must be finite")
        return parsed

    try:
        insurance_paid = _parse_payment_amount(insurance_paid_raw)
        customer_paid = _parse_payment_amount(customer_paid_raw)
    except (TypeError, ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": "insurance_paid and customer_paid must be valid currency values"},
        )

    if insurance_paid < 0 or customer_paid < 0:
        return JSONResponse(status_code=400, content={"error": "payment amounts cannot be negative"})

    business_date_value = None
    if business_date_raw:
        raw_date = business_date_raw[:10]
        try:
            business_date_value = date.fromisoformat(raw_date)
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "business_date must be YYYY-MM-DD"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_payment_totals_table(cur)
        _ensure_ro_payment_entries_table(cur)

        cur.execute(
            """
            SELECT grand_total
            FROM saved_estimates
            WHERE domain = %s
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        ro_row = cur.fetchone()
        if not ro_row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        grand_total = _parse_float_value(ro_row.get("grand_total"))

        cur.execute(
            """
            SELECT insurance_paid, customer_paid
            FROM ro_payment_totals
            WHERE domain = %s
              AND ro = %s
            LIMIT 1
            """,
            (domain, ro_value),
        )
        existing_row = cur.fetchone() or {}
        existing_insurance_paid = _parse_float_value(existing_row.get("insurance_paid"))
        existing_customer_paid = _parse_float_value(existing_row.get("customer_paid"))

        insurance_entry_amount = 0.0
        customer_entry_amount = 0.0

        if has_incremental_values:
            try:
                insurance_entry_amount = _parse_payment_amount(insurance_payment_raw)
                customer_entry_amount = _parse_payment_amount(customer_payment_raw)
            except (TypeError, ValueError):
                return JSONResponse(
                    status_code=400,
                    content={"error": "insurance_payment and customer_payment must be valid currency values"},
                )

            if insurance_entry_amount < 0 or customer_entry_amount < 0:
                return JSONResponse(status_code=400, content={"error": "payment amounts cannot be negative"})

            insurance_paid = existing_insurance_paid + insurance_entry_amount
            customer_paid = existing_customer_paid + customer_entry_amount

        cur.execute(
            """
            INSERT INTO ro_payment_totals (ro, domain, insurance_paid, customer_paid, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (domain, ro)
            DO UPDATE SET
                insurance_paid = EXCLUDED.insurance_paid,
                customer_paid = EXCLUDED.customer_paid,
                updated_at = CURRENT_TIMESTAMP
            """,
            (ro_value, domain, insurance_paid, customer_paid),
        )

        if insurance_entry_amount > 0:
            cur.execute(
                """
                INSERT INTO ro_payment_entries (ro, domain, payer_type, amount, business_date, created_at)
                VALUES (%s, %s, 'insurance', %s, %s, CURRENT_TIMESTAMP)
                """,
                (ro_value, domain, insurance_entry_amount, business_date_value),
            )

        if customer_entry_amount > 0:
            cur.execute(
                """
                INSERT INTO ro_payment_entries (ro, domain, payer_type, amount, business_date, created_at)
                VALUES (%s, %s, 'customer', %s, %s, CURRENT_TIMESTAMP)
                """,
                (ro_value, domain, customer_entry_amount, business_date_value),
            )

        conn.commit()

        balance = max(0.0, grand_total - insurance_paid - customer_paid)
        return {
            "status": "success",
            "ro": ro_value,
            "insurance_paid": insurance_paid,
            "customer_paid": customer_paid,
            "insurance_payment_saved": insurance_entry_amount,
            "customer_payment_saved": customer_entry_amount,
            "grand_total": grand_total,
            "balance": balance,
        }
    finally:
        cur.close()


@router.post("/payments/close-ro")
async def close_ro_from_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = str(data.get("ro") or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    conn = get_conn()
    cur = conn.cursor()
    previous_autocommit = conn.autocommit

    try:
        conn.autocommit = False

        _ensure_saved_estimates_table(cur)
        _ensure_closed_ro_archive_table(cur)

        cur.execute(
            """
            SELECT 1
            FROM saved_estimates
            WHERE domain = %s
              AND ro = %s
            LIMIT 1
            """,
            (domain, ro_value),
        )
        existing_ro = cur.fetchone()
        if not existing_ro:
            conn.rollback()
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        cur.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND column_name IN ('ro', 'domain')
            GROUP BY table_name
            HAVING COUNT(DISTINCT column_name) = 2
            ORDER BY table_name
            """
        )
        ro_table_rows = cur.fetchall() or []

        excluded_tables = {"closed_ro_archive"}
        archived_rows_by_table = {}
        deleted_counts = {}

        for row in ro_table_rows:
            table_name = str(row.get("table_name") or "").strip()
            if not table_name or table_name in excluded_tables:
                continue

            select_stmt = sql.SQL("SELECT * FROM {} WHERE domain = %s AND ro = %s").format(
                sql.Identifier(table_name)
            )
            cur.execute(select_stmt, (domain, ro_value))
            table_rows = cur.fetchall() or []

            if not table_rows:
                continue

            archived_rows_by_table[table_name] = [
                _to_archive_json_value(dict(table_row))
                for table_row in table_rows
            ]

            delete_stmt = sql.SQL("DELETE FROM {} WHERE domain = %s AND ro = %s").format(
                sql.Identifier(table_name)
            )
            cur.execute(delete_stmt, (domain, ro_value))
            deleted_counts[table_name] = cur.rowcount

        archived_payload = {
            "ro": ro_value,
            "domain": domain,
            "tables": archived_rows_by_table,
        }
        cur.execute(
            """
            INSERT INTO closed_ro_archive (ro, domain, archived_payload, closed_at)
            VALUES (%s, %s, %s::jsonb, CURRENT_TIMESTAMP)
            """,
            (ro_value, domain, json.dumps(archived_payload)),
        )

        conn.commit()
        return {
            "status": "success",
            "ro": ro_value,
            "archived_tables": sorted(list(archived_rows_by_table.keys())),
            "deleted": deleted_counts,
        }
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        conn.autocommit = previous_autocommit
        cur.close()


@router.get("/payments/log")
async def get_ro_payment_log(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "entries": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required", "entries": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)

        cur.execute(
            """
            SELECT
                paid_at,
                COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned') AS tech_name,
                COALESCE(SUM(pay_amount), 0) AS amount
            FROM ro_flagout_lines
            WHERE domain = %s
              AND ro = %s
              AND paid_at IS NOT NULL
            GROUP BY paid_at, COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned')
            ORDER BY paid_at DESC, tech_name ASC
            """,
            (domain, ro_value),
        )
        rows = cur.fetchall() or []

        entries = []
        for row in rows:
            paid_at = row.get("paid_at")
            if isinstance(paid_at, datetime):
                paid_display = paid_at.strftime("%Y-%m-%d %I:%M %p")
            elif isinstance(paid_at, date):
                paid_display = paid_at.isoformat()
            else:
                paid_display = str(paid_at or "")

            entries.append(
                {
                    "paid_at": paid_display,
                    "tech_name": row.get("tech_name") or "Unassigned",
                    "amount": _parse_float_value(row.get("amount")),
                }
            )

        return {"entries": entries}
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
        _ensure_ro_activity_log_table(cur)
        cur.execute(
            """
            SELECT id, owner_info, phone_original, phone_override
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
        old_phone = (row.get("phone_override") or parsed_phone or "").strip()
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

        if old_phone != new_phone:
            old_display = old_phone or "-"
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "phone_changed",
                f"Phone changed: {old_display} → {new_phone}",
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
        _ensure_ro_activity_log_table(cur)
        cur.execute(
            """
            SELECT id, in_date, ecd_date
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

        old_in_date = _coerce_date(row.get("in_date"))
        old_ecd_date = _coerce_date(row.get("ecd_date"))

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

        old_value = old_in_date if field == "in_date" else old_ecd_date
        if old_value != parsed_date:
            label = "In-date" if field == "in_date" else "ECD"
            old_display = old_value.isoformat() if old_value else "-"
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "date_changed",
                f"{label} changed: {old_display} → {parsed_date.isoformat()}",
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
        _ensure_ro_activity_log_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
            (domain, ro_value),
        )
        before_rows = cur.fetchall() or []
        before_by_type = {
            _normalize_repair_type(row.get("repair_type")): _parse_float_value(row.get("total_hours"))
            for row in before_rows
        }
        before_total_assigned = sum(before_by_type.values())

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
        _ensure_ro_activity_log_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
            (domain, ro_value),
        )
        before_rows = cur.fetchall() or []
        before_by_type = {
            _normalize_repair_type(row.get("repair_type")): _parse_float_value(row.get("total_hours"))
            for row in before_rows
        }
        before_total_assigned = sum(before_by_type.values())

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
        _ensure_ro_activity_log_table(cur)
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
            (domain, ro_value),
        )
        before_rows = cur.fetchall() or []
        before_by_type = {
            _normalize_repair_type(row.get("repair_type")): _parse_float_value(row.get("total_hours"))
            for row in before_rows
        }
        before_total_assigned = sum(before_by_type.values())

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

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
            (domain, ro_value),
        )
        after_rows = cur.fetchall() or []
        after_by_type = {
            _normalize_repair_type(row.get("repair_type")): _parse_float_value(row.get("total_hours"))
            for row in after_rows
        }
        after_total_assigned = sum(after_by_type.values())

        type_label_map = {
            "body": "Body",
            "paint": "Paint",
            "mech": "Mechanical",
            "frame": "Frame",
        }

        if selected_ids:
            tech_label = (target_tech_name or "").strip()
            if not tech_label and target_tech_id:
                tech_label = f"Tech #{target_tech_id}"
            role_label = type_label_map.get(target_type, target_type.title())
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "tech_assignment",
                f"{role_label} tech assigned → {tech_label or 'Unassigned'}",
            )

        for repair_type in sorted(set(before_by_type.keys()) | set(after_by_type.keys())):
            before_hours = before_by_type.get(repair_type, 0.0)
            after_hours = after_by_type.get(repair_type, 0.0)
            if abs(before_hours - after_hours) < 1e-6:
                continue
            role_label = type_label_map.get(repair_type, repair_type.title())
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "assigned_hours_changed",
                f"Assigned hours changed ({role_label}): {before_hours:.1f} → {after_hours:.1f}",
            )

        if abs(before_total_assigned - after_total_assigned) >= 1e-6:
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "total_assigned_hours_changed",
                f"Total assigned hours changed: {before_total_assigned:.1f} → {after_total_assigned:.1f}",
            )

        conn.commit()
        return {"status": "ok"}
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
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
                    "status": "Assigned",
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
                                hours,
                                repair_type
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro = %s
              AND tech_id = %s
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
                    "repair_type": _normalize_repair_type(row.get("repair_type")),
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
              AND COALESCE(ready_to_flag, FALSE) = FALSE
              AND line_key = ANY(%s)
            """,
            (domain, ro_value, tech_id, normalized_keys),
        )
        rows = cur.fetchall()

        if not rows:
            return JSONResponse(status_code=404, content={"error": "No matching unpaid assigned lines found"})

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
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        cur.close()


@router.post("/tech-flag-out-ros")
async def tech_flag_out_ros(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    tech_id = data.get("tech_id")
    selected_ros = data.get("ros") or []
    pay_rate = _parse_float_value(data.get("pay_rate"))

    if not tech_id:
        return JSONResponse(status_code=400, content={"error": "tech_id is required"})

    ro_values = []
    for value in selected_ros:
        ro_value = (value or "").strip()
        if ro_value and ro_value not in ro_values:
            ro_values.append(ro_value)

    if not ro_values:
        return JSONResponse(status_code=400, content={"error": "ros is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_line_assignments_table(cur)
        _ensure_ro_flagout_lines_table(cur)

        total_flagged_count = 0
        total_flagged_hours = 0.0
        total_flagged_pay = 0.0

        for ro_value in ro_values:
            _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)
            cur.execute(
                """
                SELECT id, line_key, line_number, description, hours, tech_name, repair_type
                FROM ro_line_assignments
                WHERE domain = %s
                  AND ro = %s
                  AND tech_id = %s
                  AND COALESCE(ready_to_flag, FALSE) = FALSE
                """,
                (domain, ro_value, tech_id),
            )
            rows = cur.fetchall() or []
            if not rows:
                continue

            row_ids = [int(row.get("id")) for row in rows if row.get("id") is not None]
            for row in rows:
                line_hours = _parse_float_value(row.get("hours"))
                line_pay = line_hours * pay_rate
                total_flagged_hours += line_hours
                total_flagged_pay += line_pay
                total_flagged_count += 1

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

        conn.commit()

        if total_flagged_count == 0:
            return JSONResponse(status_code=404, content={"error": "No matching unpaid assigned lines found for selected ROs"})

        return {
            "status": "ok",
            "flagged_count": total_flagged_count,
            "flagged_hours": total_flagged_hours,
            "flagged_pay": total_flagged_pay,
            "ros": ro_values,
        }
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
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
        _ensure_techs_table(cur)

        cur.execute(
            """
            SELECT
                f.tech_id,
                COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text)) AS tech_name,
                                COALESCE(MAX(NULLIF(TRIM(t.role), '')), '') AS role,
                COALESCE(MAX(f.pay_rate), 0) AS pay_rate,
                COALESCE(SUM(f.hours), 0) AS total_hours,
                COALESCE(SUM(f.pay_amount), 0) AS total_pay
            FROM ro_flagout_lines f
                        LEFT JOIN techs t
                            ON t.id = f.tech_id
                         AND (t.domain = %s OR t.domain IS NULL)
            WHERE f.domain = %s
              AND f.status = 'ready_to_flag'
            GROUP BY f.tech_id
            ORDER BY COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text))
            """,
                        (domain, domain),
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
                    "role": (row.get("role") or "").strip(),
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "total_pay": _parse_float_value(row.get("total_pay")),
                    "ros": ro_map.get(tech_id, []),
                }
            )

        return {"techs": techs}
    finally:
        cur.close()


@router.post("/flagout/payout")
async def save_flagout_payout(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selections = data.get("selections") or []
    if not isinstance(selections, list) or not selections:
        return JSONResponse(status_code=400, content={"error": "No payout selections provided"})

    normalized = []
    for item in selections:
        if not isinstance(item, dict):
            continue
        try:
            tech_id = int(item.get("tech_id"))
        except Exception:
            continue
        ros = [str(ro).strip() for ro in (item.get("ros") or []) if str(ro).strip()]
        if not ros:
            continue
        normalized.append({"tech_id": tech_id, "ros": sorted(set(ros))})

    if not normalized:
        return JSONResponse(status_code=400, content={"error": "No valid payout selections provided"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)
        _ensure_saved_estimates_table(cur)

        summaries = []

        for group in normalized:
            tech_id = group["tech_id"]
            ro_values = group["ros"]

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
                    COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text)) AS tech_name,
                    f.ro,
                    COALESCE(MAX(f.pay_rate), 0) AS pay_rate,
                    COALESCE(SUM(f.hours), 0) AS total_hours,
                    COALESCE(SUM(f.pay_amount), 0) AS total_pay,
                    MAX(le.year) AS year,
                    MAX(le.make) AS make,
                    MAX(le.model) AS model,
                    MAX(le.vehicle) AS vehicle
                FROM ro_flagout_lines f
                LEFT JOIN latest_estimates le ON le.ro = f.ro
                WHERE f.domain = %s
                  AND f.status = 'ready_to_flag'
                  AND f.tech_id = %s
                  AND f.ro = ANY(%s)
                GROUP BY f.tech_id, f.ro
                ORDER BY f.ro
                """,
                (domain, domain, tech_id, ro_values),
            )
            ro_rows = cur.fetchall() or []
            if not ro_rows:
                continue

            ro_items = []
            total_paid = 0.0
            for row in ro_rows:
                year = (row.get("year") or "").strip()
                make = (row.get("make") or "").strip()
                model = (row.get("model") or "").strip()
                vehicle_info = " ".join(part for part in [year, make, model] if part)
                if not vehicle_info:
                    vehicle_info = (row.get("vehicle") or "").strip()

                pay_rate = _parse_float_value(row.get("pay_rate"))
                total_hours = _parse_float_value(row.get("total_hours"))
                total = _parse_float_value(row.get("total_pay"))
                total_paid += total

                ro_items.append(
                    {
                        "ro": row.get("ro") or "",
                        "vehicle_info": vehicle_info,
                        "pay_rate": pay_rate,
                        "total_hours": total_hours,
                        "total": total,
                    }
                )

            tech_name = (ro_rows[0].get("tech_name") or f"Tech #{tech_id}").strip()
            pay_rate_display = _parse_float_value(ro_rows[0].get("pay_rate"))

            summaries.append(
                {
                    "tech_id": tech_id,
                    "tech_name": tech_name,
                    "total_ros_paid": len(ro_items),
                    "pay_rate": pay_rate_display,
                    "total_paid": total_paid,
                    "ros": ro_items,
                }
            )

            cur.execute(
                """
                UPDATE ro_flagout_lines
                SET status = 'paid',
                    paid_at = CURRENT_TIMESTAMP
                WHERE domain = %s
                  AND status = 'ready_to_flag'
                  AND tech_id = %s
                  AND ro = ANY(%s)
                """,
                (domain, tech_id, ro_values),
            )

        conn.commit()
        return {"status": "ok", "summaries": summaries}
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
        _ensure_ro_activity_log_table(cur)

        cur.execute(
            """
            SELECT phase
            FROM ro_phases
            WHERE ro = %s AND domain = %s
            """,
            (ro, domain),
        )
        prev_row = cur.fetchone() or {}
        previous_phase = (prev_row.get("phase") or "").strip().lower()

        cur.execute(
            """
            INSERT INTO ro_phases (ro, phase, domain)
            VALUES (%s, %s, %s)
            ON CONFLICT (ro, domain)
            DO UPDATE SET phase = EXCLUDED.phase, updated_at = CURRENT_TIMESTAMP
            """,
            (ro, phase, domain),
        )

        if previous_phase != phase:
            phase_label_map = {
                "teardown": "Teardown",
                "auth": "Auth",
                "parts": "Parts",
                "body": "Body",
                "refinish": "Refinish",
                "reassy": "Reassy",
                "sublet": "Sublet",
                "washqc": "Wash/QC",
                "wash/qc": "Wash/QC",
                "complete": "Complete/Finish",
                "complete/finish": "Complete/Finish",
            }
            old_label = phase_label_map.get(previous_phase, previous_phase or "Unassigned")
            new_label = phase_label_map.get(phase, phase or "Unassigned")
            _log_ro_activity(
                cur,
                domain,
                ro,
                "phase_changed",
                f"Phase changed: {old_label} → {new_label}",
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
            SELECT note, created_at, created_by
            FROM ro_notes
            WHERE ro = %s AND domain = %s
            ORDER BY created_at DESC
            """,
            (ro, domain),
        )
        rows = cur.fetchall()
        notes = []
        for row in rows:
            notes.append(
                {
                    "note": row.get("note"),
                    "created_at": _serialize_datetime_for_client(row.get("created_at")),
                    "created_by": _resolve_note_created_by(cur, row.get("created_by")),
                }
            )
        return {"notes": notes}
    finally:
        cur.close()


@router.get("/ro-activity")
async def list_ro_activity(request: Request, ro: str):
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
        _ensure_ro_activity_log_table(cur)
        _ensure_ro_flagout_lines_table(cur)

        timeline = []

        def add_entry(message: str, when_value) -> None:
            if not message:
                return
            ts = _activity_to_datetime(when_value)
            timeline.append(
                {
                    "date": ts.date().isoformat(),
                    "message": message,
                    "_ts": ts,
                }
            )

        cur.execute(
            """
            SELECT saved_at, in_date, ecd_date, labor_repairs, paint_repairs
            FROM saved_estimates
            WHERE domain = %s
              AND ro = %s
            ORDER BY saved_at ASC, id ASC
            """,
            (domain, ro_value),
        )
        estimate_rows = cur.fetchall() or []

        if estimate_rows:
            first_saved_at = estimate_rows[0].get("saved_at")
            add_entry("RO uploaded", first_saved_at)

            prev_total_hours = None
            prev_in_date = None
            prev_ecd_date = None
            for row in estimate_rows:
                labor_repairs = _parse_json_field(row.get("labor_repairs"))
                paint_repairs = _parse_json_field(row.get("paint_repairs"))
                labor_hours = _sum_hours(labor_repairs if isinstance(labor_repairs, list) else [])
                paint_hours = _sum_hours(paint_repairs if isinstance(paint_repairs, list) else [])
                total_hours = labor_hours + paint_hours

                current_in_date = _coerce_date(row.get("in_date"))
                current_ecd_date = _coerce_date(row.get("ecd_date"))
                saved_at = row.get("saved_at")

                if prev_total_hours is not None and abs(total_hours - prev_total_hours) >= 1e-6:
                    add_entry(f"Total hours changed: {prev_total_hours:.1f} → {total_hours:.1f}", saved_at)

                if prev_in_date is not None and current_in_date != prev_in_date:
                    old_display = prev_in_date.isoformat() if prev_in_date else "-"
                    new_display = current_in_date.isoformat() if current_in_date else "-"
                    add_entry(f"In-date changed: {old_display} → {new_display}", saved_at)

                if prev_ecd_date is not None and current_ecd_date != prev_ecd_date:
                    old_display = prev_ecd_date.isoformat() if prev_ecd_date else "-"
                    new_display = current_ecd_date.isoformat() if current_ecd_date else "-"
                    add_entry(f"ECD changed: {old_display} → {new_display}", saved_at)

                prev_total_hours = total_hours
                prev_in_date = current_in_date
                prev_ecd_date = current_ecd_date

        cur.execute(
            """
            SELECT activity_type, message, occurred_on, created_at
            FROM ro_activity_log
            WHERE domain = %s
              AND ro = %s
            ORDER BY created_at DESC, id DESC
            """,
            (domain, ro_value),
        )
        activity_rows = cur.fetchall() or []
        for row in activity_rows:
            add_entry(row.get("message") or "", row.get("created_at") or row.get("occurred_on"))

        cur.execute(
            """
            SELECT
                COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned') AS tech_name,
                paid_at,
                COALESCE(SUM(pay_amount), 0) AS total_paid
            FROM ro_flagout_lines
            WHERE domain = %s
              AND ro = %s
              AND paid_at IS NOT NULL
            GROUP BY COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned'), paid_at
            ORDER BY paid_at DESC
            """,
            (domain, ro_value),
        )
        payment_rows = cur.fetchall() or []
        for row in payment_rows:
            tech_name = row.get("tech_name") or "Unassigned"
            total_paid = _parse_float_value(row.get("total_paid"))
            add_entry(f"Payment made ({tech_name}): ${total_paid:,.2f}", row.get("paid_at"))

        timeline.sort(key=lambda item: item.get("_ts") or datetime.min, reverse=True)

        deduped = []
        seen = set()
        for item in timeline:
            key = (item.get("date"), item.get("message"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append({"date": item.get("date"), "message": item.get("message")})

        return {"entries": deduped}
    finally:
        cur.close()


@router.post("/ro-notes")
async def add_ro_note(request: Request):
    domain = get_user_domain(request) or "default"
    session_user = getattr(request.state, "user", {}) or {}
    first_name = str(session_user.get("first_name") or "").strip()
    last_name = str(session_user.get("last_name") or "").strip()
    full_name = " ".join(part for part in (first_name, last_name) if part)
    created_by = full_name or str(session_user.get("email") or "").strip() or "Unknown"
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
            INSERT INTO ro_notes (ro, note, domain, created_by)
            VALUES (%s, %s, %s, %s)
            """,
            (ro, note, domain, created_by),
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
        _ensure_ro_line_assignments_table(cur)

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

        cur.execute(
            """
            SELECT ro, line_id
            FROM parts_received
            WHERE domain = %s
              AND COALESCE(returned, FALSE) = FALSE
            """,
            (domain,),
        )
        received_not_returned_rows = cur.fetchall() or []
        received_not_returned_by_ro = {}
        for received_row in received_not_returned_rows:
            ro_value = received_row.get("ro")
            line_id = received_row.get("line_id")
            if not ro_value or line_id is None:
                continue
            try:
                line_num = int(line_id)
            except (TypeError, ValueError):
                continue
            received_not_returned_by_ro.setdefault(ro_value, set()).add(line_num)

        cur.execute(
            """
            SELECT ro, COUNT(*) as returned
            FROM parts_received
            WHERE domain = %s
              AND COALESCE(returned, FALSE) = TRUE
            GROUP BY ro
            """,
            (domain,),
        )
        returned_rows = cur.fetchall() or []
        returned_map = {row["ro"]: int(row.get("returned") or 0) for row in returned_rows}

        cur.execute(
            """
            SELECT ro, repair_type, tech_name
            FROM ro_line_assignments
            WHERE domain = %s
              AND ro IS NOT NULL
              AND ro <> ''
              AND tech_name IS NOT NULL
              AND TRIM(tech_name) <> ''
            ORDER BY ro, CASE WHEN repair_type = 'body' THEN 0 WHEN repair_type = 'paint' THEN 1 ELSE 2 END
            """,
            (domain,),
        )
        tech_rows = cur.fetchall() or []
        tech_by_ro = {}
        for tech_row in tech_rows:
            ro_value = tech_row.get("ro")
            if not ro_value or ro_value in tech_by_ro:
                continue
            tech_by_ro[ro_value] = (tech_row.get("tech_name") or "").strip()

        order_summary = {}
        on_order_warning_counts = {}
        today = date.today()
        for order in orders:
            ro = order["ro"]
            if ro not in order_summary:
                order_summary[ro] = {
                    "ordered_ids": set(),
                    "arrival_date": order.get("arrival_date"),
                    "included_line_ids": set(),
                }

            ordered_ids = _normalize_line_ids(order.get("ordered_lines") or [])
            order_summary[ro]["ordered_ids"].update(ordered_ids)

            received_not_returned_ids = received_not_returned_by_ro.get(ro, set())
            included_line_ids = order_summary[ro]["included_line_ids"]

            eta_date = order.get("arrival_date")
            created_at = order.get("created_at")
            created_date = created_at.date() if isinstance(created_at, datetime) else today

            for line_id in ordered_ids:
                if line_id in included_line_ids:
                    continue
                included_line_ids.add(line_id)

                if line_id in received_not_returned_ids:
                    continue

                if eta_date:
                    threshold_date = eta_date + timedelta(days=1)
                else:
                    threshold_date = created_date + timedelta(days=2)

                if today > threshold_date:
                    on_order_warning_counts[ro] = on_order_warning_counts.get(ro, 0) + 1

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
            ordered_ids = summary.get("ordered_ids", set())
            returned_count = returned_map.get(ro, 0)
            on_order = max(0, len(ordered_ids) - returned_count)
            ros.append(
                {
                    "ro": ro,
                    "vehicle": row.get("vehicle"),
                    "tech": tech_by_ro.get(ro, "—"),
                    "parts_qty": float(parts_qty or line_count or 0),
                    "on_order": on_order,
                    "on_order_warning_count": on_order_warning_counts.get(ro, 0),
                    "arrival_date": summary.get("arrival_date"),
                    "arrived": received_map.get(ro, 0),
                    "returned": returned_count,
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
        _ensure_parts_orders_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT ordered_lines
            FROM parts_orders
            WHERE domain = %s AND ro = %s
            """,
            (domain, ro),
        )
        order_rows = cur.fetchall() or []
        ordered_ids = set()
        for order_row in order_rows:
            ordered_ids.update(_normalize_line_ids(order_row.get("ordered_lines") or []))

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE domain = %s AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (domain, ro),
        )
        received_rows = cur.fetchall() or []
        received_not_returned_ids = {
            int(received_row.get("line_id"))
            for received_row in received_rows
            if received_row.get("line_id") is not None
        }

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE domain = %s AND ro = %s AND COALESCE(returned, FALSE) = TRUE
            """,
            (domain, ro),
        )
        returned_rows = cur.fetchall() or []
        returned_ids = {
            int(returned_row.get("line_id"))
            for returned_row in returned_rows
            if returned_row.get("line_id") is not None
        }

        blocked_ids = (ordered_ids - returned_ids) | received_not_returned_ids

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
            parsed_description, parsed_part_number = _parse_part_description_and_number(item)
            explicit_part_number = (
                item.get("part_number")
                or item.get("part_no")
                or item.get("part#")
                or item.get("pn")
                or ""
            )
            part_number = str(parsed_part_number or explicit_part_number or "").strip()
            lines.append(
                {
                    "id": idx,
                    "line": item.get("line"),
                    "description": parsed_description,
                    "part_number": part_number,
                    "part_type": item.get("part_type"),
                    "price": float(item.get("price") or 0),
                    "qty": float(item.get("qty") or 0),
                    "is_ordered": idx in blocked_ids,
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
    ordered_lines = _normalize_line_ids(data.get("ordered_lines") or [])

    if not ro:
        return JSONResponse(status_code=400, content={"error": "RO is required"})
    if not ordered_lines:
        return JSONResponse(status_code=400, content={"error": "No parts selected"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_orders_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT ordered_lines
            FROM parts_orders
            WHERE domain = %s AND ro = %s
            """,
            (domain, ro),
        )
        existing_orders = cur.fetchall() or []
        already_ordered = set()
        for existing_order in existing_orders:
            already_ordered.update(_normalize_line_ids(existing_order.get("ordered_lines") or []))

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE domain = %s AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (domain, ro),
        )
        received_rows = cur.fetchall() or []
        received_not_returned_ids = {
            int(received_row.get("line_id"))
            for received_row in received_rows
            if received_row.get("line_id") is not None
        }

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE domain = %s AND ro = %s AND COALESCE(returned, FALSE) = TRUE
            """,
            (domain, ro),
        )
        returned_rows = cur.fetchall() or []
        returned_ids = {
            int(returned_row.get("line_id"))
            for returned_row in returned_rows
            if returned_row.get("line_id") is not None
        }

        unavailable_ids = (already_ordered - returned_ids) | received_not_returned_ids
        duplicate_lines = sorted(line_id for line_id in ordered_lines if line_id in unavailable_ids)
        if duplicate_lines:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Some selected lines are already on order and not returned",
                    "duplicate_lines": duplicate_lines,
                },
            )

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
                json.dumps(sorted(ordered_lines)),
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
            SELECT line_id, vendor, part_number, list_price, cost, eta, invoice_number, invoice_total, returned, received_at
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
                "part_number": row.get("part_number"),
                "list": float(row.get("list_price") or 0),
                "cost": float(row.get("cost") or 0),
                "eta": row.get("eta").isoformat() if row.get("eta") else None,
                "invoice_number": row.get("invoice_number"),
                "invoice_total": float(row.get("invoice_total") or 0),
                "returned": bool(row.get("returned")),
                "received_at": row.get("received_at"),
            }
            for row in rows
        ]
        return {"items": items}
    finally:
        cur.close()


@router.get("/parts/arrived-lines")
async def list_arrived_lines(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_received_table(cur)
        _ensure_saved_estimates_table(cur)

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        estimate_row = cur.fetchone()
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs")) if estimate_row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        metadata_by_line = {}
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            parsed_description, parsed_part_number = _parse_part_description_and_number(item)
            metadata_by_line[idx] = {
                "line": item.get("line") or idx,
                "description": parsed_description,
                "part_number": parsed_part_number,
                "list": float(item.get("price") or 0),
            }

        cur.execute(
            """
                                                SELECT line_id, vendor, part_number, list_price, cost, invoice_number, received_business_date, received_at
            FROM parts_received
            WHERE domain = %s
              AND ro = %s
              AND COALESCE(returned, FALSE) = FALSE
                        ORDER BY COALESCE(received_business_date, received_at::date) DESC, line_id
            """,
            (domain, ro_value),
        )
        rows = cur.fetchall() or []

        items = []
        for row in rows:
            line_id = int(row.get("line_id") or 0)
            metadata = metadata_by_line.get(line_id, {})
            items.append(
                {
                    "line_id": line_id,
                    "line": metadata.get("line") or line_id,
                    "description": metadata.get("description") or "",
                    "part_number": row.get("part_number") or metadata.get("part_number") or "",
                    "list": float(row.get("list_price") or metadata.get("list") or 0),
                    "vendor": row.get("vendor") or "",
                    "cost": float(row.get("cost") or 0),
                    "invoice_number": row.get("invoice_number") or "",
                    "arrived_date": (
                        row.get("received_business_date").isoformat() if row.get("received_business_date")
                        else (row.get("received_at").date().isoformat() if row.get("received_at") else None)
                    ),
                    "received_at": row.get("received_at").isoformat() if row.get("received_at") else None,
                }
            )

        return {"items": items}
    finally:
        cur.close()


@router.post("/parts/arrived-return")
async def return_arrived_lines(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    line_ids = _normalize_line_ids(data.get("line_ids") or [])
    local_business_date_text = (data.get("local_business_date") or "").strip()

    local_business_date = None
    if local_business_date_text:
        try:
            local_business_date = datetime.strptime(local_business_date_text[:10], "%Y-%m-%d").date()
        except ValueError:
            local_business_date = None

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required"})
    if not line_ids:
        return JSONResponse(status_code=400, content={"error": "Select at least one line"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_received_table(cur)
        _ensure_parts_orders_table(cur)

        updated_count = 0
        for line_id in line_ids:
            cur.execute(
                """
                UPDATE parts_received
                                SET returned = TRUE,
                                                                                returned_at = CURRENT_TIMESTAMP,
                                                                                returned_business_date = COALESCE(%s, CURRENT_DATE)
                WHERE domain = %s
                  AND ro = %s
                  AND line_id = %s
                  AND COALESCE(returned, FALSE) = FALSE
                """,
                                (local_business_date, domain, ro_value, line_id),
            )
            updated_count += int(cur.rowcount or 0)

        cur.execute(
            """
            UPDATE parts_orders
            SET
                returned_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                      AND COALESCE(pr.returned, FALSE) = TRUE
                ),
                arrived_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                )
            WHERE parts_orders.domain = %s
              AND parts_orders.ro = %s
            """,
            (domain, ro_value),
        )

        conn.commit()
        return {"status": "ok", "returned_count": updated_count}
    finally:
        cur.close()


@router.get("/parts/returned-lines")
async def list_returned_lines(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_received_table(cur)
        _ensure_saved_estimates_table(cur)

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        estimate_row = cur.fetchone()
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs")) if estimate_row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        line_metadata = {}
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            parsed_description, parsed_part_number = _parse_part_description_and_number(item)
            line_metadata[idx] = {
                "line": item.get("line") or idx,
                "description": parsed_description,
                "part_number": parsed_part_number,
            }

        cur.execute(
            """
                        SELECT line_id, vendor, part_number, cost, returned_business_date, returned_at, received_business_date, received_at
            FROM parts_received
            WHERE domain = %s
              AND ro = %s
              AND COALESCE(returned, FALSE) = TRUE
                        ORDER BY COALESCE(returned_business_date, returned_at::date, received_business_date, received_at::date) DESC, line_id
            """,
            (domain, ro_value),
        )
        rows = cur.fetchall() or []

        items = []
        for row in rows:
            line_id = int(row.get("line_id") or 0)
            metadata = line_metadata.get(line_id, {})
            return_date_value = (
                row.get("returned_business_date")
                or (row.get("returned_at").date() if row.get("returned_at") else None)
                or row.get("received_business_date")
                or (row.get("received_at").date() if row.get("received_at") else None)
            )
            items.append(
                {
                    "line_id": line_id,
                    "line": metadata.get("line") or line_id,
                    "description": metadata.get("description") or "",
                    "part_number": row.get("part_number") or metadata.get("part_number") or "",
                    "vendor": row.get("vendor") or "",
                    "cost": float(row.get("cost") or 0),
                    "return_date": return_date_value.isoformat() if return_date_value else None,
                }
            )

        return {"items": items}
    finally:
        cur.close()


@router.get("/parts/on-order-lines")
async def list_on_order_lines(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_parts_orders_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE domain = %s AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (domain, ro_value),
        )
        received_rows = cur.fetchall() or []
        received_ids = {
            int(received_row.get("line_id"))
            for received_row in received_rows
            if received_row.get("line_id") is not None
        }

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        estimate_row = cur.fetchone()
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs")) if estimate_row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        line_metadata = {}
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            parsed_description, part_number = _parse_part_description_and_number(item)
            line_metadata[idx] = {
                "line": item.get("line") or idx,
                "description": parsed_description,
                "part_number": str(part_number or ""),
                "qty": float(item.get("qty") or 0),
                "list": float(item.get("price") or 0),
            }

        cur.execute(
            """
            SELECT id, vendor_name, arrival_date, ordered_lines
            FROM parts_orders
            WHERE domain = %s AND ro = %s
            ORDER BY created_at DESC, id DESC
            """,
            (domain, ro_value),
        )
        order_rows = cur.fetchall() or []

        items = []
        included_line_ids = set()
        for order_row in order_rows:
            order_id = order_row.get("id")
            vendor_name = order_row.get("vendor_name") or ""
            arrival_date = order_row.get("arrival_date")
            ordered_line_ids = _normalize_line_ids(order_row.get("ordered_lines") or [])

            for line_id in sorted(ordered_line_ids):
                if line_id in received_ids or line_id in included_line_ids:
                    continue
                metadata = line_metadata.get(line_id, {})
                items.append(
                    {
                        "order_id": order_id,
                        "line_id": line_id,
                        "line": metadata.get("line") or line_id,
                        "description": metadata.get("description") or "",
                        "part_number": metadata.get("part_number") or "",
                        "qty": float(metadata.get("qty") or 0),
                        "list": float(metadata.get("list") or 0),
                        "vendor": vendor_name,
                        "eta": arrival_date.isoformat() if arrival_date else None,
                    }
                )
                included_line_ids.add(line_id)

        return {"items": items}
    finally:
        cur.close()


@router.post("/parts/on-order-receive")
async def receive_on_order_lines(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    vendor_name_input = (data.get("vendor") or "").strip()
    invoice_number = (data.get("invoice_number") or "").strip()
    invoice_total_amount = data.get("invoice_total_amount")
    local_business_date_text = (data.get("local_business_date") or "").strip()
    items = data.get("items") or []

    local_business_date = None
    if local_business_date_text:
        try:
            local_business_date = datetime.strptime(local_business_date_text[:10], "%Y-%m-%d").date()
        except ValueError:
            local_business_date = None

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required"})
    if not vendor_name_input:
        return JSONResponse(status_code=400, content={"error": "Vendor is required"})
    if not invoice_number:
        return JSONResponse(status_code=400, content={"error": "Invoice number is required"})
    if not isinstance(items, list) or len(items) == 0:
        return JSONResponse(status_code=400, content={"error": "Select at least one part"})

    try:
        invoice_total = float(invoice_total_amount)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "Total invoice amount is invalid"})

    selected_cost_total = 0.0
    normalized_items = []
    for item in items:
        try:
            order_id = int(item.get("order_id"))
            line_id = int(item.get("line_id"))
            cost = float(item.get("cost"))
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "Invalid selected item data"})

        vendor = vendor_name_input or (item.get("vendor") or "").strip()
        if not vendor:
            return JSONResponse(status_code=400, content={"error": "Vendor is required for selected lines"})

        part_number = (item.get("part_number") or "").strip()
        qty_received_value = item.get("qty_received")
        try:
            qty_received = float(qty_received_value)
        except (TypeError, ValueError):
            qty_received = 1.0
        if qty_received <= 0:
            return JSONResponse(status_code=400, content={"error": "Received quantity must be greater than zero"})

        list_value = item.get("list")
        try:
            list_price = float(list_value) if list_value not in (None, "") else None
        except (TypeError, ValueError):
            list_price = None

        eta_value = (item.get("eta") or "").strip()
        eta_date = None
        if eta_value:
            try:
                eta_date = datetime.strptime(eta_value[:10], "%Y-%m-%d").date()
            except ValueError:
                eta_date = None

        selected_cost_total += cost
        normalized_items.append(
            {
                "order_id": order_id,
                "line_id": line_id,
                "cost": cost,
                "vendor": vendor,
                "part_number": part_number,
                "qty_received": qty_received,
                "list_price": list_price,
                "eta": eta_date,
            }
        )

    if round(selected_cost_total, 2) != round(invoice_total, 2):
        return JSONResponse(status_code=400, content={"error": "Selected part costs must equal total invoice amount"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_orders_table(cur)
        _ensure_parts_received_table(cur)

        line_ids_by_order = {}
        for item in normalized_items:
            order_id = item["order_id"]
            line_ids_by_order.setdefault(order_id, set()).add(item["line_id"])

        for order_id, selected_line_ids in line_ids_by_order.items():
            cur.execute(
                """
                SELECT ordered_lines
                FROM parts_orders
                WHERE id = %s AND domain = %s AND ro = %s
                LIMIT 1
                """,
                (order_id, domain, ro_value),
            )
            order_row = cur.fetchone()
            if not order_row:
                return JSONResponse(status_code=400, content={"error": "Order item no longer available"})

            existing_ids = _normalize_line_ids(order_row.get("ordered_lines") or [])
            if not selected_line_ids.issubset(existing_ids):
                return JSONResponse(status_code=400, content={"error": "Some selected lines are no longer on order"})

        for item in normalized_items:
            cur.execute(
                """
                INSERT INTO parts_received
                    (ro, line_id, vendor, part_number, qty_received, list_price, cost, eta, invoice_number, invoice_total, returned, received_business_date, domain)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, COALESCE(%s, CURRENT_DATE), %s)
                ON CONFLICT (ro, line_id, domain)
                DO UPDATE SET
                    vendor = EXCLUDED.vendor,
                    part_number = EXCLUDED.part_number,
                    qty_received = EXCLUDED.qty_received,
                    list_price = EXCLUDED.list_price,
                    cost = EXCLUDED.cost,
                    eta = EXCLUDED.eta,
                    invoice_number = EXCLUDED.invoice_number,
                    invoice_total = EXCLUDED.invoice_total,
                    returned = FALSE,
                    received_business_date = EXCLUDED.received_business_date,
                    received_at = CURRENT_TIMESTAMP
                """,
                (
                    ro_value,
                    item["line_id"],
                    item["vendor"],
                    item["part_number"] or None,
                    item["qty_received"],
                    item["list_price"],
                    item["cost"],
                    item["eta"],
                    invoice_number,
                    invoice_total,
                    local_business_date,
                    domain,
                ),
            )

        for order_id, selected_line_ids in line_ids_by_order.items():
            cur.execute(
                """
                SELECT ordered_lines
                FROM parts_orders
                WHERE id = %s AND domain = %s AND ro = %s
                LIMIT 1
                """,
                (order_id, domain, ro_value),
            )
            order_row = cur.fetchone()
            if not order_row:
                continue

            existing_ids = _normalize_line_ids(order_row.get("ordered_lines") or [])
            remaining_ids = sorted(existing_ids - selected_line_ids)
            if remaining_ids:
                cur.execute(
                    """
                    UPDATE parts_orders
                    SET ordered_lines = %s
                    WHERE id = %s
                    """,
                    (json.dumps(remaining_ids), order_id),
                )
            else:
                cur.execute("DELETE FROM parts_orders WHERE id = %s", (order_id,))

        cur.execute(
            """
            UPDATE parts_orders
            SET
                returned_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                      AND COALESCE(pr.returned, FALSE) = TRUE
                ),
                arrived_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                )
            WHERE parts_orders.domain = %s
              AND parts_orders.ro = %s
            """,
            (domain, ro_value),
        )

        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()


@router.get("/vendors/invoices")
async def list_vendor_invoices(request: Request, vendor_id: int):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "invoices": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        _ensure_parts_received_table(cur)

        cur.execute(
            """
            SELECT name
            FROM parts_vendors
            WHERE id = %s AND domain = %s AND active = TRUE
            LIMIT 1
            """,
            (vendor_id, domain),
        )
        vendor_row = cur.fetchone()
        if not vendor_row:
            return JSONResponse(status_code=404, content={"error": "Vendor not found", "invoices": []})

        vendor_name = (vendor_row.get("name") or "").strip()
        if not vendor_name:
            return {"invoices": []}

        cur.execute(
            """
            SELECT
                ro AS invoice_number,
                MAX(COALESCE(received_business_date, received_at::date)) AS invoice_date,
                COALESCE(SUM(cost), 0) AS total_cost
            FROM parts_received
            WHERE domain = %s
              AND LOWER(TRIM(vendor)) = LOWER(TRIM(%s))
            GROUP BY ro
            ORDER BY MAX(COALESCE(received_business_date, received_at::date)) DESC
            """,
            (domain, vendor_name),
        )
        rows = cur.fetchall() or []

        invoices = [
            {
                "date": row.get("invoice_date").isoformat() if row.get("invoice_date") else None,
                "invoice_number": row.get("invoice_number"),
                "total_cost": float(row.get("total_cost") or 0),
            }
            for row in rows
        ]

        return {"invoices": invoices}
    finally:
        cur.close()


@router.get("/vendors/invoice-parts")
async def list_vendor_invoice_parts(request: Request, vendor_id: int, invoice_number: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "parts": []})

    invoice_value = (invoice_number or "").strip()
    if not invoice_value:
        return JSONResponse(status_code=400, content={"error": "invoice_number is required", "parts": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        _ensure_parts_received_table(cur)
        _ensure_saved_estimates_table(cur)

        cur.execute(
            """
            SELECT name
            FROM parts_vendors
            WHERE id = %s AND domain = %s AND active = TRUE
            LIMIT 1
            """,
            (vendor_id, domain),
        )
        vendor_row = cur.fetchone()
        if not vendor_row:
            return JSONResponse(status_code=404, content={"error": "Vendor not found", "parts": []})

        vendor_name = (vendor_row.get("name") or "").strip()
        if not vendor_name:
            return {"parts": []}

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, invoice_value),
        )
        estimate_row = cur.fetchone()
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs")) if estimate_row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        line_lookup = {}
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            line_lookup[idx] = {
                "line": item.get("line") or idx,
                "description": item.get("description") or "",
            }

        cur.execute(
            """
            SELECT line_id, cost, received_at
            FROM parts_received
            WHERE domain = %s
              AND ro = %s
              AND LOWER(TRIM(vendor)) = LOWER(TRIM(%s))
            ORDER BY line_id
            """,
            (domain, invoice_value, vendor_name),
        )
        rows = cur.fetchall() or []
        parts = []
        for row in rows:
            line_id = int(row.get("line_id") or 0)
            metadata = line_lookup.get(line_id, {})
            parts.append(
                {
                    "line_id": line_id,
                    "line": metadata.get("line") or line_id,
                    "description": metadata.get("description") or "",
                    "cost": float(row.get("cost") or 0),
                    "received_at": row.get("received_at").isoformat() if row.get("received_at") else None,
                }
            )

        return {"parts": parts}
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
            returned = bool(item.get("returned"))
            if not line_id or not vendor:
                continue
            cur.execute(
                """
                INSERT INTO parts_received (ro, line_id, vendor, cost, returned, domain)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (ro, line_id, vendor, cost, returned, domain),
            )

        cur.execute(
            """
            UPDATE parts_orders
            SET
                returned_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                      AND COALESCE(pr.returned, FALSE) = TRUE
                ),
                arrived_count = (
                    SELECT COUNT(*)
                    FROM parts_received pr
                    WHERE pr.domain = parts_orders.domain
                      AND pr.ro = parts_orders.ro
                )
            WHERE parts_orders.domain = %s
              AND parts_orders.ro = %s
            """,
            (domain, ro),
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


@router.get("/ro-estimate")
async def get_ro_estimate_snapshot(request: Request, ro: str):
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
        cur.execute(
            """
            SELECT
                ro,
                vehicle,
                year,
                make,
                model,
                vin,
                owner_info,
                insurance_company,
                claim_number,
                estimator,
                written_by,
                labor_repairs,
                paint_repairs,
                parts_repairs,
                estimate_totals,
                estimate_snapshot,
                saved_at
            FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (domain, ro_value),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})

        labor_repairs = _parse_json_field(row.get("labor_repairs"))
        paint_repairs = _parse_json_field(row.get("paint_repairs"))
        parts_repairs = _parse_json_field(row.get("parts_repairs"))

        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        saved_snapshot = _parse_json_field(row.get("estimate_snapshot"))
        if isinstance(saved_snapshot, dict) and saved_snapshot:
            saved_unified_lines = _build_unified_estimate_lines(saved_snapshot)
            legacy_unified_lines = _build_unified_estimate_lines(
                {
                    "sections": [
                        {"key": "labor", "items": labor_repairs},
                        {"key": "paint", "items": paint_repairs},
                        {"key": "parts", "items": parts_repairs},
                    ]
                }
            )
            saved_snapshot["unified_lines"] = _merge_unified_lines(saved_unified_lines, legacy_unified_lines)
            return {"estimate": saved_snapshot}

        totals = _parse_json_field(row.get("estimate_totals"))
        if not isinstance(totals, dict):
            totals = {}

        fallback_snapshot = {
            "version": 1,
            "source": "fallback",
            "header": {
                "ro": row.get("ro") or ro_value,
                "claim_number": row.get("claim_number") or "",
                "vehicle": {
                    "year": row.get("year") or "",
                    "make": row.get("make") or "",
                    "model": row.get("model") or "",
                    "vin": row.get("vin") or "",
                    "raw": row.get("vehicle") or "",
                },
                "owner_info": row.get("owner_info") or "",
                "insurance_company": row.get("insurance_company") or "",
                "estimator": row.get("estimator") or row.get("written_by") or "",
                "saved_at": _serialize_datetime_for_client(row.get("saved_at")),
            },
            "sections": [
                {
                    "key": "labor",
                    "title": "Labor Repairs",
                    "items": labor_repairs,
                },
                {
                    "key": "paint",
                    "title": "Refinish Repairs",
                    "items": paint_repairs,
                },
                {
                    "key": "parts",
                    "title": "Parts Replacements",
                    "items": parts_repairs,
                },
            ],
            "totals": totals,
        }
        fallback_snapshot["unified_lines"] = _build_unified_estimate_lines(fallback_snapshot)
        return {"estimate": fallback_snapshot}
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
