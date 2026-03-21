from fastapi import Request
from app.services.middleware import get_user_domain

from .auth_utils import _resolve_request_user_email
from .db_schema import _ensure_shop_users_table
from .parsing_utils import _line_key, _normalize_repair_type
from .payments_utils import _parse_float_value, _parse_json_field


def _resolve_note_created_by(cur, value: str) -> str:
    created_by = str(value or "").strip()
    if not created_by:
        return "Unknown"
    return created_by


def _resolve_request_user_display_name(request: Request, cur, domain: str | None = None) -> str:
    email = _resolve_request_user_email(request)
    normalized_email = str(email or "").strip().lower()
    if not normalized_email:
        return "System"

    resolved_domain = str(domain or "").strip().lower()
    if not resolved_domain:
        resolved_domain = str(get_user_domain(request) or "").strip().lower()

    try:
        _ensure_shop_users_table(cur)
        if resolved_domain:
            cur.execute(
                """
                SELECT first_name, last_name
                FROM shop_users
                WHERE domain = %s
                  AND LOWER(email) = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (resolved_domain, normalized_email),
            )
        else:
            cur.execute(
                """
                SELECT first_name, last_name
                FROM shop_users
                WHERE LOWER(email) = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (normalized_email,),
            )
        row = cur.fetchone() or {}
    except Exception:
        row = {}

    first_name = str(row.get("first_name") or "").strip()
    last_name = str(row.get("last_name") or "").strip()
    full_name = " ".join(part for part in (first_name, last_name) if part).strip()
    if full_name:
        return full_name
    return normalized_email


def _load_latest_repairs_for_ro(
    cur,
    domain: str,
    ro_value: str,
    shop_id: int | None = None,
    shop_uuid: str | None = None,
) -> tuple[list, list]:
    if shop_id and shop_uuid:
        cur.execute(
            """
            SELECT labor_repairs, paint_repairs
            FROM saved_estimates
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (shop_uuid, shop_id, domain, ro_value),
        )
    else:
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


def _upsert_ro_lines(
    cur,
    domain: str,
    ro_value: str,
    repair_type: str,
    lines: list,
    shop_id: int | None = None,
    shop_uuid: str | None = None,
) -> None:
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
        if shop_id and shop_uuid:
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
                    domain,
                    shop_id,
                    shop_uuid
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, FALSE, %s, %s, %s::uuid)
                ON CONFLICT (ro, source_repair_type, line_key, domain)
                DO UPDATE SET
                    line_number = EXCLUDED.line_number,
                    description = EXCLUDED.description,
                    hours = EXCLUDED.hours,
                    shop_id = EXCLUDED.shop_id,
                    shop_uuid = EXCLUDED.shop_uuid,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (ro_value, normalized_type, normalized_type, line_key, line_number, description, hours, domain, shop_id, shop_uuid),
            )
        else:
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


def _ensure_ro_line_assignments_for_ro(
    cur,
    domain: str,
    ro_value: str,
    shop_id: int | None = None,
    shop_uuid: str | None = None,
) -> None:
    labor_repairs, paint_repairs = _load_latest_repairs_for_ro(
        cur,
        domain,
        ro_value,
        shop_id=shop_id,
        shop_uuid=shop_uuid,
    )
    _upsert_ro_lines(
        cur,
        domain,
        ro_value,
        "body",
        labor_repairs,
        shop_id=shop_id,
        shop_uuid=shop_uuid,
    )
    _upsert_ro_lines(
        cur,
        domain,
        ro_value,
        "paint",
        paint_repairs,
        shop_id=shop_id,
        shop_uuid=shop_uuid,
    )


def _get_scope_rows(
    cur,
    domain: str,
    ro_value: str,
    source: dict,
    shop_id: int,
    shop_uuid: str,
) -> list:
    mode = (source.get("mode") or "").strip().lower()
    if mode == "unassigned":
        repair_type = _normalize_repair_type(source.get("repair_type"))
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
              AND tech_name IS NULL
              AND COALESCE(is_pending, FALSE) = FALSE
              AND repair_type = %s
            """,
            (shop_uuid, shop_id, domain, ro_value, repair_type),
        )
        return cur.fetchall()

    if mode == "pending":
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
              AND tech_name IS NULL
              AND COALESCE(is_pending, FALSE) = TRUE
            """,
            (shop_uuid, shop_id, domain, ro_value),
        )
        return cur.fetchall()

    if mode == "tech":
        repair_type = _normalize_repair_type(source.get("repair_type"))
        tech_name = (source.get("tech_name") or "").strip()
        cur.execute(
            """
            SELECT id, repair_type, line_key
            FROM ro_line_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
              AND tech_name = %s
              AND repair_type = %s
            """,
            (shop_uuid, shop_id, domain, ro_value, tech_name, repair_type),
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
