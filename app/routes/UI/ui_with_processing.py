from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf, extract_words_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import process_pdf_grid, generate_pages_html
from app.services.db import get_conn
from app.services.middleware import get_user_domain
from .flagout import get_flagtech_screen_html
from .parts import get_parts_screen_html, get_parts_script
from .techs import get_techs_screen_html
from .phase import get_phase_screen_html
try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script
    from .upload_ui.save_estimate import (
        get_save_estimate_modal_html,
        get_save_estimate_modal_styles,
        get_save_estimate_modal_script,
    )
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script
    from save_estimate import (
        get_save_estimate_modal_html,
        get_save_estimate_modal_styles,
        get_save_estimate_modal_script,
    )
import math
import re
import json
import hashlib
from datetime import date, timedelta

router = APIRouter()


def _ensure_estimate_uploads_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS estimate_uploads (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            estimate_hash VARCHAR(64) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_estimate_uploads_ro_domain ON estimate_uploads(ro, domain)")


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
            vin VARCHAR(32),
            claim_number VARCHAR(64),
            phone_original TEXT,
            phone_override TEXT,
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
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS vin VARCHAR(32)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS claim_number VARCHAR(64)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_original TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_override TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS written_by TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimator TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS ecd_date DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_ro_domain ON saved_estimates(ro, domain)")


def _parse_money(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _to_float(value, default: float = 0.0) -> float:
    try:
        parsed = float(str(value).replace(",", "").strip())
        if math.isfinite(parsed):
            return parsed
    except Exception:
        pass
    return default


def _line_key_for_item(item: dict, index: int) -> str:
    if not isinstance(item, dict):
        return str(index + 1)
    value = item.get("line")
    if value is None or str(value).strip() == "":
        return str(index + 1)
    return str(value).strip()


def _normalize_text(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


_PART_TOKEN_RE = re.compile(r"^[A-Z0-9-]{5,}$", re.IGNORECASE)
_WORD_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")


def _normalize_operation(value: str) -> str:
    token = _normalize_text(value).upper()
    token = token.replace(" ", "")
    token = token.replace("R/I", "R&I")
    token = token.replace("R\I", "R&I")
    if token in {"REPLACE", "REPL"}:
        token = "REPL"
    if token in {"R&I", "O/H", "REPL"}:
        return token
    if re.fullmatch(r"S\d{1,3}", token):
        return token
    return token


def _looks_like_part_number(token: str) -> bool:
    if not _PART_TOKEN_RE.fullmatch(token or ""):
        return False
    has_alpha = any(char.isalpha() for char in token)
    has_digit = any(char.isdigit() for char in token)
    return has_alpha and has_digit


def _parse_line_components(operation_value, description_value, part_number_value) -> tuple[str, str, str]:
    description = _normalize_text(description_value)
    tokens = description.split()

    operation = _normalize_operation(str(operation_value or ""))
    if not operation and tokens:
        candidate = _normalize_operation(tokens[0])
        if candidate in {"R&I", "O/H", "REPL"} or re.fullmatch(r"S\d{1,3}", candidate):
            operation = candidate
            tokens = tokens[1:]

    part_number = _normalize_text(part_number_value).upper()
    if not part_number and tokens:
        candidate = tokens[-1].strip().upper()
        if _looks_like_part_number(candidate):
            part_number = candidate
            tokens = tokens[:-1]

    description_core = _normalize_text(" ".join(tokens))
    return operation, description_core, part_number


def _line_identity(operation_value, description_value, part_number_value) -> tuple[str, str, str]:
    operation, description_core, part_number = _parse_line_components(
        operation_value,
        description_value,
        part_number_value,
    )
    return operation, description_core.lower(), part_number


def _description_tokens(value: str) -> set[str]:
    tokens = []
    for piece in _WORD_SPLIT_RE.split(str(value or "").lower()):
        token = piece.strip()
        if not token:
            continue
        if token in {"the", "and", "for", "w", "with", "to", "a", "an", "of"}:
            continue
        tokens.append(token)
    return set(tokens)


def _description_similarity(left: str, right: str) -> float:
    left_tokens = _description_tokens(left)
    right_tokens = _description_tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    union = left_tokens | right_tokens
    if not union:
        return 0.0
    return len(left_tokens & right_tokens) / len(union)


def _line_match_score(new_identity: tuple[str, str, str], old_identity: tuple[str, str, str]) -> float:
    new_op, new_desc, new_part = new_identity
    old_op, old_desc, old_part = old_identity

    if new_op == old_op and new_desc == old_desc and new_part == old_part:
        return 100.0

    desc_similarity = _description_similarity(new_desc, old_desc)
    op_match = bool(new_op and old_op and new_op == old_op)
    part_match = bool(new_part and old_part and new_part == old_part)

    if op_match and part_match and desc_similarity >= 0.30:
        return 85.0 + (desc_similarity * 10.0)

    if op_match and desc_similarity >= 0.65:
        return 70.0 + (desc_similarity * 10.0)

    if part_match and desc_similarity >= 0.65:
        return 65.0 + (desc_similarity * 10.0)

    if desc_similarity >= 0.90:
        return 60.0 + (desc_similarity * 10.0)

    return 0.0


def _canonical_labor_or_paint_lines(items) -> dict:
    result = {}
    if not isinstance(items, list):
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        line_key = _line_key_for_item(item, index)
        result[line_key] = {
            "line": line_key,
            "description": _normalize_text(item.get("description")),
            "value": round(_to_float(item.get("value"), 0.0), 4),
        }
    return result


def _canonical_parts_lines(items) -> dict:
    result = {}
    if not isinstance(items, list):
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        line_key = _line_key_for_item(item, index)
        result[line_key] = {
            "line": line_key,
            "description": _normalize_text(item.get("description")),
            "part_type": _normalize_text(item.get("part_type")).upper(),
            "price": round(_to_float(item.get("price"), 0.0), 4),
            "qty": round(_to_float(item.get("qty"), 0.0), 4),
        }
    return result


def _canonical_totals(totals: dict | None) -> dict:
    source = totals if isinstance(totals, dict) else {}
    keys = [
        "parts_total",
        "grand_total",
        "deductible",
        "customer_pay",
        "insurance_pay",
        "body_labor",
        "paint_labor",
        "frame_labor",
        "mechanical_labor",
        "glass_labor",
    ]
    return {key: round(_to_float(source.get(key), 0.0), 4) for key in keys}


def _estimate_has_changes_against_saved(saved_row: dict | None, labor_items, paint_items, parts_items, estimate_totals: dict) -> bool:
    if not saved_row:
        return True

    saved_labor = _canonical_labor_or_paint_lines(saved_row.get("labor_repairs"))
    saved_paint = _canonical_labor_or_paint_lines(saved_row.get("paint_repairs"))
    saved_parts = _canonical_parts_lines(saved_row.get("parts_repairs"))
    saved_totals = _canonical_totals(saved_row.get("estimate_totals"))

    new_labor = _canonical_labor_or_paint_lines(labor_items)
    new_paint = _canonical_labor_or_paint_lines(paint_items)
    new_parts = _canonical_parts_lines(parts_items)
    new_totals = _canonical_totals(estimate_totals)

    if saved_labor != new_labor:
        return True
    if saved_paint != new_paint:
        return True
    if saved_parts != new_parts:
        return True
    if saved_totals != new_totals:
        return True
    return False


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
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_assignments_ro_role_domain
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
            ready_to_flag BOOLEAN DEFAULT FALSE,
            flagged_at TIMESTAMP,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS source_repair_type VARCHAR(20)")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS is_pending BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS ready_to_flag BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS flagged_at TIMESTAMP")
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


def _sync_ro_line_assignments_for_estimate_update(cur, domain: str, ro_value: str, labor_repairs, paint_repairs) -> list[dict]:
    cur.execute(
        """
        SELECT repair_type, source_repair_type, description, tech_id, tech_name, is_pending, ready_to_flag, flagged_at
        FROM ro_line_assignments
        WHERE domain = %s
          AND ro = %s
          AND COALESCE(source_repair_type, repair_type) IN ('body', 'paint')
        """,
        (domain, ro_value),
    )
    old_rows = cur.fetchall() or []

    old_pool = []
    for row in old_rows:
        old_pool.append(
            {
                "identity": _line_identity("", row.get("description"), ""),
                "tech_id": row.get("tech_id"),
                "tech_name": (row.get("tech_name") or "").strip(),
                "is_pending": bool(row.get("is_pending")),
                "ready_to_flag": bool(row.get("ready_to_flag")),
                "flagged_at": row.get("flagged_at"),
            }
        )

    cur.execute(
        """
        DELETE FROM ro_line_assignments
        WHERE domain = %s
          AND ro = %s
          AND COALESCE(source_repair_type, repair_type) IN ('body', 'paint')
        """,
        (domain, ro_value),
    )

    inserted_rows = []

    def _insert_role_lines(items, repair_type: str) -> None:
        if not isinstance(items, list):
            return
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            line_key = _line_key_for_item(item, index)
            line_number = str(item.get("line") or line_key)
            description = _normalize_text(item.get("description"))
            hours = _to_float(item.get("value"), 0.0)

            new_identity = _line_identity(
                item.get("operation"),
                description,
                item.get("part_number") or item.get("partNumber") or item.get("part_no") or "",
            )
            best_index = -1
            best_score = 0.0
            for idx, candidate in enumerate(old_pool):
                score = _line_match_score(new_identity, candidate.get("identity") or ("", "", ""))
                if score > best_score:
                    best_score = score
                    best_index = idx

            prior_match = None
            if best_index >= 0 and best_score >= 60.0:
                prior_match = old_pool.pop(best_index)

            tech_id = prior_match.get("tech_id") if prior_match else None
            tech_name = prior_match.get("tech_name") if prior_match else None
            if tech_name == "":
                tech_name = None
            is_pending = bool(prior_match.get("is_pending")) if prior_match and not tech_name else False
            ready_to_flag = bool(prior_match.get("ready_to_flag")) if prior_match and tech_name else False
            flagged_at = prior_match.get("flagged_at") if prior_match and ready_to_flag else None

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
                    ready_to_flag,
                    flagged_at,
                    domain
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING line_key, repair_type, hours, tech_id, tech_name
                """,
                (
                    ro_value,
                    repair_type,
                    repair_type,
                    line_key,
                    line_number,
                    description,
                    hours,
                    tech_id,
                    tech_name,
                    is_pending,
                    ready_to_flag,
                    flagged_at,
                    domain,
                ),
            )
            inserted = cur.fetchone() or {}
            inserted_rows.append(
                {
                    "line_key": str(inserted.get("line_key") or line_key),
                    "repair_type": (inserted.get("repair_type") or repair_type).strip().lower(),
                    "hours": _to_float(inserted.get("hours"), hours),
                    "tech_id": inserted.get("tech_id"),
                    "tech_name": (inserted.get("tech_name") or "").strip(),
                }
            )

    _insert_role_lines(labor_repairs, "body")
    _insert_role_lines(paint_repairs, "paint")
    return inserted_rows


def _sum_hours_with_excluded(items, excluded_lines) -> float:
    if not isinstance(items, list):
        return 0.0
    excluded = {str(value).strip() for value in (excluded_lines or [])}
    total = 0.0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        line_key = _line_key_for_item(item, index)
        if line_key in excluded:
            continue
        total += _to_float(item.get("value"), 0.0)
    return total


def _recalculate_ro_assignment_hours(cur, domain: str, ro_value: str, labor_repairs, paint_repairs) -> None:
    cur.execute(
        """
        SELECT id, role, excluded_lines
        FROM ro_assignments
        WHERE domain = %s AND ro = %s
        """,
        (domain, ro_value),
    )
    rows = cur.fetchall() or []
    for row in rows:
        role = str(row.get("role") or "").strip().lower()
        excluded = row.get("excluded_lines")
        if not isinstance(excluded, list):
            try:
                excluded = json.loads(excluded) if excluded else []
            except Exception:
                excluded = []
        if role == "labor":
            assigned_hours = _sum_hours_with_excluded(labor_repairs, excluded)
        elif role == "paint":
            assigned_hours = _sum_hours_with_excluded(paint_repairs, excluded)
        else:
            continue
        cur.execute(
            """
            UPDATE ro_assignments
            SET assigned_hours = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (assigned_hours, row.get("id")),
        )


def _refresh_role_assignments_from_lines(cur, domain: str, ro_value: str, inserted_rows: list[dict]) -> None:
    role_rows = {
        "labor": [row for row in inserted_rows if row.get("repair_type") == "body"],
        "paint": [row for row in inserted_rows if row.get("repair_type") == "paint"],
    }

    cur.execute(
        """
        SELECT id, role, tech_id, tech_name
        FROM ro_assignments
        WHERE domain = %s AND ro = %s AND role IN ('labor', 'paint')
        """,
        (domain, ro_value),
    )
    assignment_rows = cur.fetchall() or []

    for assignment in assignment_rows:
        role = (assignment.get("role") or "").strip().lower()
        rows = role_rows.get(role, [])
        assignment_tech_id = assignment.get("tech_id")
        assignment_tech_name = (assignment.get("tech_name") or "").strip()

        excluded = []
        assigned_hours = 0.0
        for row in rows:
            row_line_key = str(row.get("line_key") or "").strip()
            row_tech_id = row.get("tech_id")
            row_tech_name = (row.get("tech_name") or "").strip()

            is_assigned_to_role_tech = False
            if assignment_tech_id is not None and row_tech_id is not None:
                is_assigned_to_role_tech = int(assignment_tech_id) == int(row_tech_id)
            elif assignment_tech_name and row_tech_name:
                is_assigned_to_role_tech = assignment_tech_name == row_tech_name

            if is_assigned_to_role_tech:
                assigned_hours += _to_float(row.get("hours"), 0.0)
            else:
                excluded.append(row_line_key)

        cur.execute(
            """
            UPDATE ro_assignments
            SET excluded_lines = %s::jsonb,
                assigned_hours = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (json.dumps(excluded), assigned_hours, assignment.get("id")),
        )


def _safe_json(payload) -> str:
    return json.dumps(payload).replace("<", "\\u003c")


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


def _estimate_hours_for_ecd(payload: dict) -> float:
    labor_repairs = payload.get("labor_repairs") or []
    paint_repairs = payload.get("paint_repairs") or []
    total = 0.0

    def _to_float(value) -> float:
        try:
            return float(str(value).replace(",", ""))
        except Exception:
            return 0.0

    for item in labor_repairs:
        if isinstance(item, dict):
            total += _to_float(item.get("value") or 0)
    for item in paint_repairs:
        if isinstance(item, dict):
            total += _to_float(item.get("value") or 0)
    return total

@router.get("/", response_class=HTMLResponse)
async def home_screen():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>FlagTech</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            background-color: #f2f2f2;
        }}
        .sidebar {{
            width: 150px;
            background-color: #d32f2f;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        .nav-box {{
            padding: 15px;
            background-color: #d32f2f;
            color: white;
            text-align: center;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        .nav-box:hover {{
            background-color: #b22222;
            border: 2px solid white;
        }}
        .nav-box.active {{
            background-color: #d32f2f;
            color: white;
            border: 2px solid #d32f2f;
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            margin-left: 150px;
            background-color: #f2f2f2;
            min-height: 100vh;
        }}
        .screen {{
            display: none;
        }}
        .screen.active {{
            display: block;
        }}
        :root {{
            --app-bg: #a9a9a9;
            --card-bg: #e4e4e4;
        }}
        body,
        .content-area,
        .screen {{
            background-color: var(--app-bg) !important;
        }}
        [style*="background:#d32f2f"],
        [style*="background: #d32f2f"],
        [style*="background-color:#d32f2f"],
        [style*="background-color: #d32f2f"],
        [style*="background:#b22222"],
        [style*="background: #b22222"],
        [style*="background-color:#b22222"],
        [style*="background-color: #b22222"],
        [style*="background:#505050"],
        [style*="background: #505050"],
        [style*="background-color:#505050"],
        [style*="background-color: #505050"],
        [style*="background:#666666"],
        [style*="background: #666666"],
        [style*="background-color:#666666"],
        [style*="background-color: #666666"],
        [style*="background:#707070"],
        [style*="background: #707070"],
        [style*="background-color:#707070"],
        [style*="background-color: #707070"] {{
            background: var(--app-bg) !important;
            background-color: var(--app-bg) !important;
        }}
        .modal-content,
        .dash-center-card,
        .dash-mini-card,
        .mini-popup-panel,
        .phase-card,
        .phase-cards,
        #estimateSummary,
        #flagoutTechTable,
        #techsTableContainer,
        #statusDropdownMenu,
        [style*="background:#fff"],
        [style*="background: #fff"],
        [style*="background-color:#fff"],
        [style*="background-color: #fff"],
        [style*="background:#f9f9f9"],
        [style*="background: #f9f9f9"],
        [style*="background-color:#f9f9f9"],
        [style*="background-color: #f9f9f9"],
        [style*="background:#f2f2f2"],
        [style*="background: #f2f2f2"],
        [style*="background-color:#f2f2f2"],
        [style*="background-color: #f2f2f2"],
        [style*="background:#f0f0f0"],
        [style*="background: #f0f0f0"],
        [style*="background-color:#f0f0f0"],
        [style*="background-color: #f0f0f0"],
        [style*="background:#f5f5f5"],
        [style*="background: #f5f5f5"],
        [style*="background-color:#f5f5f5"],
        [style*="background-color: #f5f5f5"],
        [style*="background:#f7f7f7"],
        [style*="background: #f7f7f7"],
        [style*="background-color:#f7f7f7"],
        [style*="background-color: #f7f7f7"],
        [style*="background:#fafafa"],
        [style*="background: #fafafa"],
        [style*="background-color:#fafafa"],
        [style*="background-color: #fafafa"],
        [style*="background:#e0e0e0"],
        [style*="background: #e0e0e0"],
        [style*="background-color:#e0e0e0"],
        [style*="background-color: #e0e0e0"],
        [style*="background:#d9d9d9"],
        [style*="background: #d9d9d9"],
        [style*="background-color:#d9d9d9"],
        [style*="background-color: #d9d9d9"] {{
            background: var(--card-bg) !important;
            background-color: var(--card-bg) !important;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="nav-box active" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-box" onclick="switchScreen('tech')">TECHS</div>
        <div class="nav-box" onclick="switchScreen('phase')">ROADMAP</div>
        <div class="nav-box" onclick="switchScreen('parts')">PARTS</div>
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        {get_upload_screen_html()}
        {get_parts_screen_html()}
        {get_techs_screen_html()}
        {get_phase_screen_html()}
        {get_flagtech_screen_html()}
    </div>
    
    <script>
        function normalizeFormAccessibility(root = document) {{
            const fields = root.querySelectorAll('input, select, textarea');
            let counter = window.__flagtechFieldCounter || 0;

            fields.forEach((field) => {{
                const type = (field.getAttribute('type') || '').toLowerCase();
                if (!field.id) {{
                    counter += 1;
                    field.id = `ft-field-${{counter}}`;
                }}
                if (!field.name && !['button', 'submit', 'reset', 'image'].includes(type)) {{
                    field.name = field.id;
                }}
            }});

            window.__flagtechFieldCounter = counter;

            const labels = Array.from(root.querySelectorAll('label'));
            labels.forEach((label) => {{
                if (label.htmlFor) return;

                let target = label.querySelector('input, select, textarea');
                if (!target && label.nextElementSibling && label.nextElementSibling.matches('input, select, textarea')) {{
                    target = label.nextElementSibling;
                }}

                if (target) {{
                    if (!target.id) {{
                        counter += 1;
                        target.id = `ft-field-${{counter}}`;
                    }}
                    label.htmlFor = target.id;
                }}
            }});

            window.__flagtechFieldCounter = counter;
        }}

        normalizeFormAccessibility();
        const a11yObserver = new MutationObserver(() => normalizeFormAccessibility());
        a11yObserver.observe(document.body, {{ childList: true, subtree: true }});

        function switchScreen(screenName) {{
            // Hide all screens
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));
            
            // Remove active class from all nav boxes
            const navBoxes = document.querySelectorAll('.nav-box');
            navBoxes.forEach(box => box.classList.remove('active'));
            
            // Show selected screen
            document.getElementById(screenName).classList.add('active');
            
            // Add active class to clicked nav box
            event.target.classList.add('active');

            if (screenName === 'parts' && typeof partsLoadRos === 'function') {{
                partsLoadRos();
                partsLoadVendors();
            }}

            if (screenName === 'phase' && typeof loadPhaseData === 'function') {{
                loadPhaseData();
            }}

            if (screenName === 'tech' && typeof loadTechsList === 'function') {{
                loadTechsList();
            }}

            if (screenName === 'flagtech' && typeof loadFlagoutTechs === 'function') {{
                loadFlagoutTechs();
            }}
        }}
        
        {get_upload_script()}
        {get_parts_script()}
    </script>
</body>
</html>
"""

@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FlagTech Estimate Parser</title>
</head>
<body style="font-family: Arial; padding: 40px; background-color: #f2f2f2;">
    <h2>Upload an Estimate PDF</h2>
    <form id="uploadForm" action="/ui/grid" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" onchange="this.form.submit()" />
    </form>
    <script>
        // Auto-submit form when file is selected
    </script>
</body>
</html>
"""

@router.post("/parse", response_class=HTMLResponse)
async def parse_ui(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    # Debug logging: show a truncated preview of extracted text
    try:
        print("===EXTRACTED TEXT PREVIEW (truncated)===")
        print(text[:4000])
        print("===END PREVIEW===")
    except Exception:
        print("[extractor] could not print text preview")

    items = parse_estimate_text(text)
    print(f"[parser] parsed {len(items)} items")

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item.line}</td>
            <td>{item.operation or ''}</td>
            <td>{item.description or ''}</td>
            <td>{item.labor if item.labor is not None else ''}</td>
            <td>{item.paint if item.paint is not None else ''}</td>
        </tr>
        """

    return f"""
<html>
<head>
    <title>Parsed Estimate</title>
</head>
<body style="font-family: Arial; padding: 40px; background-color: #f2f2f2;">
    <h2>Parsed Line Items</h2>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Line</th>
            <th>Op</th>
            <th>Description</th>
            <th>Labor</th>
            <th>Paint</th>
        </tr>
        {rows}
    </table>
    <br><br>
    <a href="/ui">Upload another file</a>
</body>
</html>
"""



@router.post("/grid", response_class=HTMLResponse)
async def grid_ui(request: Request, file: UploadFile = File(...), ajax: str = None):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # Process PDF using service layer
    result = process_pdf_grid(pages)
    
    # Extract results from service
    labor_items = result["labor_items"]
    paint_items = result["paint_items"]
    parts_items = result.get("parts_items", [])
    total_labor = result["total_labor"]
    total_paint = result["total_paint"]
    parts_total = result.get("parts_total")
    grand_total = result.get("grand_total")
    deductible = result.get("deductible")
    customer_pay = result.get("customer_pay")
    insurance_pay = result.get("insurance_pay")
    second_ro_line = result["second_ro_line"]
    vehicle_info_line = result["vehicle_info_line"]
    owner_info = result.get("owner_info", "")
    insurance_company = result.get("insurance_company", "")
    written_by = result.get("written_by", "")
    estimator = result.get("estimator", "")
    vin = result.get("vin", "")
    claim_number = result.get("claim_number", "")
    anchor_page = result["anchor_page"]
    anchor_ymid = result["anchor_ymid"]
    subtotals_page = result["subtotals_page"]
    subtotals_ymid = result["subtotals_ymid"]

    domain = get_user_domain(request)
    ro_number = None
    if domain:
        ro_match = re.search(r"\bRO\b.*?(\d+)", second_ro_line)
        ro_number = ro_match.group(1) if ro_match else None

    # Generate pages HTML visualization
    pages_html = generate_pages_html(pages, anchor_page, anchor_ymid, subtotals_page, subtotals_ymid)
    
    labor_items_json = _safe_json(labor_items)
    paint_items_json = _safe_json(paint_items)
    parts_items_json = _safe_json(parts_items)

    # If AJAX request, return just the content without HTML wrapper
    if ajax:
        # Generate modal HTML using imported functions
        save_estimate_modal = get_save_estimate_modal_html(
            second_ro_line,
            vehicle_info_line,
            total_labor,
            total_paint,
            parts_total,
            grand_total,
            deductible,
            customer_pay,
            insurance_pay,
            owner_info,
            insurance_company,
            vin,
            claim_number,
            estimator,
            written_by,
        )
        
        # Generate modal styles
        save_estimate_styles = get_save_estimate_modal_styles()
        
        # Generate modal scripts
        save_estimate_script = get_save_estimate_modal_script(
            labor_items_json,
            paint_items_json,
            parts_items_json,
            second_ro_line,
            vehicle_info_line,
            ro_number,
            total_labor,
            total_paint,
            parts_total,
            grand_total,
            deductible,
            customer_pay,
            insurance_pay,
            result.get("body_labor"),
            result.get("paint_labor"),
            result.get("frame_labor"),
            result.get("mechanical_labor"),
            result.get("glass_labor"),
            owner_info,
            insurance_company,
            vin,
            claim_number,
            estimator,
            written_by,
        )
        
        content = f"""
<h2>Document Visual Grid</h2>
<button onclick="openSaveEstimateModal(window.currentEstimateTotals)" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold;'>Save</button>
<br><br>
<div id="estimatePages">
{pages_html}
</div>
<br><a href='/ui'>Back</a>

{save_estimate_modal}

<style>
  .modal {{
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
  }}
    .modal-content {{
        background-color: #f2f2f2;
    margin: 2% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 95%;
    max-width: 1400px;
    height: 80vh;
    overflow-y: auto;
    border-radius: 5px;
  }}
  .close {{
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
  }}
  .close:hover {{
    color: black;
  }}
{save_estimate_styles}
</style>

<script>
{save_estimate_script}
</script>
        """
        return content


@router.post("/save-estimate")
async def save_estimate(request: Request):
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()

    ro_value = (data.get("ro_number") or data.get("ro") or "").strip()
    match = re.search(r"\bRO\b\s*[:#-]*\s*([A-Za-z0-9-]+)", ro_value)
    if match:
        ro_value = match.group(1)

    estimate_totals = data.get("estimate_totals") or {}
    labor_repairs = data.get("labor_repairs") or []
    paint_repairs = data.get("paint_repairs") or []
    parts_repairs = data.get("parts_repairs") or []
    domain = get_user_domain(request)
    local_upload_date = (data.get("local_upload_date") or "").strip()
    in_date_value = date.today()
    if local_upload_date:
        try:
            in_date_value = date.fromisoformat(local_upload_date)
        except ValueError:
            in_date_value = date.today()
    ecd_date_value = _add_weekdays(in_date_value, _weekday_days_from_hours(_estimate_hours_for_ecd(data)))

    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_line_assignments_table(cur)
        _ensure_ro_assignments_table(cur)

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
        existing_row = cur.fetchone()

        if existing_row:
            cur.execute(
                """
                UPDATE saved_estimates
                SET vehicle = %s,
                    year = %s,
                    make = %s,
                    model = %s,
                    owner_info = %s,
                    insurance_company = %s,
                    vin = %s,
                    claim_number = %s,
                    written_by = %s,
                    estimator = %s,
                    in_date = %s,
                    ecd_date = %s,
                    labor_repairs = %s,
                    paint_repairs = %s,
                    parts_repairs = %s,
                    estimate_snapshot = %s,
                    estimate_totals = %s,
                    parts_total = %s,
                    grand_total = %s,
                    deductible = %s,
                    customer_pay = %s,
                    insurance_pay = %s,
                    saved_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    data.get("vehicle"),
                    data.get("year"),
                    data.get("make"),
                    data.get("model"),
                    data.get("owner_info"),
                    data.get("insurance_company"),
                    data.get("vin"),
                    data.get("claim_number"),
                    data.get("written_by"),
                    data.get("estimator"),
                    in_date_value,
                    ecd_date_value,
                    json.dumps(labor_repairs),
                    json.dumps(paint_repairs),
                    json.dumps(parts_repairs),
                    json.dumps(data.get("estimate_snapshot") or {}),
                    json.dumps(estimate_totals or {}),
                    _parse_money(estimate_totals.get("parts_total")),
                    _parse_money(estimate_totals.get("grand_total")),
                    _parse_money(estimate_totals.get("deductible")),
                    _parse_money(estimate_totals.get("customer_pay")),
                    _parse_money(estimate_totals.get("insurance_pay")),
                    existing_row.get("id"),
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO saved_estimates
                (ro, vehicle, year, make, model, owner_info, insurance_company, vin, claim_number,
                 written_by, estimator, labor_repairs, paint_repairs, parts_repairs,
                 estimate_snapshot, estimate_totals, parts_total, grand_total, deductible, customer_pay, insurance_pay, in_date, ecd_date, domain)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ro_value,
                    data.get("vehicle"),
                    data.get("year"),
                    data.get("make"),
                    data.get("model"),
                    data.get("owner_info"),
                    data.get("insurance_company"),
                    data.get("vin"),
                    data.get("claim_number"),
                    data.get("written_by"),
                    data.get("estimator"),
                    json.dumps(labor_repairs),
                    json.dumps(paint_repairs),
                    json.dumps(parts_repairs),
                    json.dumps(data.get("estimate_snapshot") or {}),
                    json.dumps(estimate_totals or {}),
                    _parse_money(estimate_totals.get("parts_total")),
                    _parse_money(estimate_totals.get("grand_total")),
                    _parse_money(estimate_totals.get("deductible")),
                    _parse_money(estimate_totals.get("customer_pay")),
                    _parse_money(estimate_totals.get("insurance_pay")),
                    in_date_value,
                    ecd_date_value,
                    domain,
                ),
            )

        inserted_rows = _sync_ro_line_assignments_for_estimate_update(cur, domain, ro_value, labor_repairs, paint_repairs)
        _refresh_role_assignments_from_lines(cur, domain, ro_value, inserted_rows)
        _recalculate_ro_assignment_hours(cur, domain, ro_value, labor_repairs, paint_repairs)
        conn.commit()
    finally:
        cur.close()

    return {"status": "success"}


@router.post("/aligned", response_class=HTMLResponse)
async def aligned_ui(file: UploadFile = File(...)):
    from app.services.grid_processor import kmeans_1d, group_rows
    
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # compute xmid/ymid and page index for all words across all pages
    all_words = []
    for pi, page in enumerate(pages, start=1):
        for wdict in page.get("words", []):
            wdict["page_index"] = pi
            wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0
            all_words.append(wdict)

    if not all_words:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # determine anchor (second RO row) and end marker (ESTIMATE TOTALS row)
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    
    for pi, page in enumerate(pages, start=1):
        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
            
            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break

    # collect all xmid values to cluster into 5 columns (global across pages)
    # if anchor found, only use words at/after anchor and before subtotals to compute centers
    if anchor_page:
        if subtotals_page:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page and w["page_index"] < subtotals_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid) or (w["page_index"] == subtotals_page and w["ymid"] <= subtotals_ymid)]
        else:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid)]
    else:
        xvals = [w["xmid"] for w in all_words]
    centers = kmeans_1d(xvals, 5, iters=40)
    if not centers:
        return "<html><body><p>Could not compute columns.</p><a href='/ui'>Back</a></body></html>"

    centers_sorted = sorted(centers)
    col_names = ["Line", "Op", "Description", "Labor", "Paint"]

    table_rows = ""
    # process pages in order and append their rows
    for page_idx, page in enumerate(pages, start=1):
        # skip pages after subtotals
        if subtotals_page and page_idx > subtotals_page:
            continue
        
        # ensure per-page xmid/ymid are present
        for wdict in page.get("words", []):
            if "xmid" not in wdict:
                wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            if "ymid" not in wdict:
                wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0

        rows = group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            # skip rows above anchor (RO) or at/below subtotals
            if anchor_page and page_idx == anchor_page and anchor_ymid is not None:
                if r["ymid"] < anchor_ymid:
                    continue
            if subtotals_page and page_idx == subtotals_page and subtotals_ymid is not None:
                if r["ymid"] >= subtotals_ymid:
                    continue
            
            # sort words in row by x
            wlist = sorted(r["words"], key=lambda ww: ww["xmid"])
            cols = {i: [] for i in range(len(centers_sorted))}
            for ww in wlist:
                # assign to nearest center
                best = min(range(len(centers_sorted)), key=lambda c: abs(ww["xmid"] - centers_sorted[c]))
                cols[best].append(ww)

            # join texts per column
            vals = []
            for i in range(len(centers_sorted)):
                part = " ".join(w["text"] for w in sorted(cols[i], key=lambda z: z["xmid"]))
                vals.append(part)

            # Filter out header/customer rows: require a leading line number in first column
            left_col = vals[0].strip() if vals else ""
            combined_text = " ".join(vals).lower()
            if not re.search(r"\b\d+\b", left_col):
                if any(k in combined_text for k in ("customer", "address", "vin", "page", "estimate", "phone", "fax", "ro")):
                    continue
                if left_col.lower() in ("line", "line#", "no", "qty"):
                    continue

            # render only the five columns
            table_rows += "<tr>"
            for i in range(5):
                table_rows += f"<td>{(vals[i] if i < len(vals) else '')}</td>"
            table_rows += "</tr>"

    header_html = "".join(f"<th>{n}</th>" for n in col_names)

    return f"""
<html>
<head><title>Aligned Table</title></head>
<body style='font-family:Arial; padding:20px;'>
  <h2>Aligned Table (All Pages)</h2>
  <table border='1' cellpadding='6' cellspacing='0'>
    <tr>{header_html}</tr>
    {table_rows}
  </table>
  <br><a href='/ui'>Back</a>
</body>
</html>
"""