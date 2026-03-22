from ._shared import (
    asyncio,
    os,
    json,
    math,
    re,
    hashlib,
    uuid,
    Decimal,
    date,
    datetime,
    timedelta,
    timezone,
    APIRouter,
    UploadFile,
    File,
    Request,
    Response,
    JSONResponse,
    load_pdf,
    parse_estimate_pdf,
    EstimateResponse,
    get_conn,
    SESSION_COOKIE_NAME,
    create_auth_session,
    get_authenticated_user,
    get_authenticated_user_email,
    get_user_domain,
    get_user_shop_uuid,
    revoke_auth_session,
    build_permission_snapshot,
    _quote_ident,
    _ensure_shops_table,
    _sync_shop_id_bindings,
    _ensure_parts_vendors_table,
    _ensure_shop_settings_table,
    _ensure_shop_users_table,
    _ensure_chat_messages_table,
    _ensure_saved_estimates_table,
    _ensure_ro_payment_totals_table,
    _ensure_ro_payment_entries_table,
    _ensure_parts_orders_table,
    _ensure_parts_received_table,
    _ensure_ro_phases_table,
    _ensure_ro_notes_table,
    _ensure_ro_activity_log_table,
    _ensure_ro_assignments_table,
    _ensure_ro_line_assignments_table,
    _ensure_ro_flagout_lines_table,
    _ensure_techs_table,
    _ensure_archived_techs_table,
    _resolve_first_active_shop_domain,
    _resolve_effective_shop_domain,
    _ensure_shop_id_columns_for_domain_tables,
    _ensure_shop_id_sync_triggers,
    _resolve_request_shop_id,
    _resolve_request_shop_uuid,
    _ensure_shop_isolation_infrastructure,
    resolve_request_scope,
    build_shop_isolation_filter,
    _resolve_request_user_email,
    _is_architect_email,
    _build_cookie_secure_flag,
    _resolve_internal_access_level,
    _request_is_architect,
    _resolve_setup_scope_domain,
    _resolve_note_created_by,
    _resolve_request_user_display_name,
    _load_latest_repairs_for_ro,
    _upsert_ro_lines,
    _ensure_ro_line_assignments_for_ro,
    _get_scope_rows,
    _sum_assigned_hours,
    _is_manager_or_hr_role,
    _parse_part_description_and_number,
    _resolve_current_user_row,
    _to_local_business_date,
    _parse_json_field,
    _parse_float_value,
    _activity_to_datetime,
    _log_ro_activity,
    _normalize_line_ids,
    _alpha_only_description,
    _serialize_datetime_for_client,
    _extract_line_number,
    _coerce_number,
    _build_unified_estimate_lines,
    _coerce_date,
    _weekday_days_from_hours,
    _add_weekdays,
    _calculate_ecd_date,
    _parse_owner_info,
    _sum_hours,
    _line_key,
    _normalize_repair_type,
)

router = APIRouter()

@router.post("/ro-phone")
async def update_ro_phone(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    action = (data.get("action") or "replace_primary").strip().lower()
    new_phone = (data.get("phone") or "").strip()
    new_email = (data.get("email") or "").strip()
    index_raw = data.get("index")
    try:
        phone_index = int(index_raw)
    except (TypeError, ValueError):
        phone_index = None

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    allowed_actions = {"replace_primary", "add_phone", "set_email", "update_phone_at_index", "delete_phone_at_index"}
    if action not in allowed_actions:
        if new_phone:
            action = "replace_primary"
        elif "email" in data:
            action = "set_email"
        else:
            return JSONResponse(status_code=400, content={"error": "invalid action"})

    if action in {"replace_primary", "add_phone", "update_phone_at_index"} and not new_phone:
        return JSONResponse(status_code=400, content={"error": "phone is required"})

    if action in {"update_phone_at_index", "delete_phone_at_index"}:
        if phone_index is None or phone_index < 0:
            return JSONResponse(status_code=400, content={"error": "valid index is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            """
            SELECT id, owner_info, phone_original, phone_override, customer_phones, customer_email
            FROM saved_estimates
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        _, parsed_phone = _parse_owner_info(row.get("owner_info") or "")
        old_email = (row.get("customer_email") or "").strip()
        stored_phone_values = _parse_json_field(row.get("customer_phones"))
        phone_numbers = []
        if isinstance(stored_phone_values, list):
            for value in stored_phone_values:
                phone_value = str(value or "").strip()
                if phone_value and phone_value not in phone_numbers:
                    phone_numbers.append(phone_value)

        if not phone_numbers:
            fallback_phone = (row.get("phone_override") or parsed_phone or "").strip()
            if fallback_phone:
                phone_numbers.append(fallback_phone)

        old_phone = phone_numbers[0] if phone_numbers else ""
        phone_original = (row.get("phone_original") or parsed_phone or old_phone or "").strip()
        old_phone_at_index = ""
        if phone_index is not None and 0 <= phone_index < len(phone_numbers):
            old_phone_at_index = str(phone_numbers[phone_index] or "").strip()

        if action == "replace_primary":
            if phone_numbers:
                phone_numbers[0] = new_phone
            else:
                phone_numbers.append(new_phone)
        elif action == "add_phone":
            if new_phone not in phone_numbers:
                phone_numbers.append(new_phone)
        elif action == "update_phone_at_index":
            if phone_index == 0 and not phone_numbers:
                phone_numbers.append(new_phone)
            elif phone_index >= len(phone_numbers):
                return JSONResponse(status_code=400, content={"error": "phone index out of range"})
            else:
                phone_numbers[phone_index] = new_phone
        elif action == "delete_phone_at_index":
            if phone_index >= len(phone_numbers):
                return JSONResponse(status_code=400, content={"error": "phone index out of range"})
            phone_numbers.pop(phone_index)

        deduped_numbers = []
        for value in phone_numbers:
            cleaned_value = str(value or "").strip()
            if cleaned_value and cleaned_value not in deduped_numbers:
                deduped_numbers.append(cleaned_value)
        phone_numbers = deduped_numbers

        updated_email = old_email
        if action == "set_email":
            updated_email = new_email

        primary_phone = phone_numbers[0] if phone_numbers else ""
        if not phone_original:
            phone_original = primary_phone

        cur.execute(
            """
            UPDATE saved_estimates
            SET phone_override = %s,
                phone_original = COALESCE(NULLIF(TRIM(phone_original), ''), %s),
                customer_phones = %s::jsonb,
                customer_email = %s
            WHERE id = %s
            """,
            (
                primary_phone or None,
                phone_original or primary_phone or None,
                json.dumps(phone_numbers),
                updated_email or None,
                row.get("id"),
            ),
        )

        if action == "replace_primary" and old_phone != new_phone:
            old_display = old_phone or "-"
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "phone_changed",
                f"Phone changed: {old_display} → {new_phone}",
            )
        elif action == "add_phone" and new_phone:
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "phone_added",
                f"Additional phone added: {new_phone}",
            )
        elif action == "update_phone_at_index" and old_phone_at_index != new_phone:
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "phone_changed",
                f"Phone changed: {old_phone_at_index or '-'} → {new_phone}",
            )
        elif action == "delete_phone_at_index":
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "phone_removed",
                f"Phone removed: {old_phone_at_index or '-'}",
            )

        if action == "set_email" and old_email != updated_email:
            old_display = old_email or "-"
            new_display = updated_email or "-"
            _log_ro_activity(
                cur,
                domain,
                ro_value,
                "email_changed",
                f"Email changed: {old_display} → {new_display}",
            )

        conn.commit()
        return {
            "status": "success",
            "phone": primary_phone,
            "phone_original": phone_original,
            "phone_numbers": phone_numbers,
            "email": updated_email,
        }
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
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
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
                            AND ro = %s
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                            )
            """,
                        (current_shop_uuid, current_shop_id, domain),
        )
        active_ids = {int(row.get("id")) for row in (cur.fetchall() or []) if row.get("id") is not None}
        cur.execute(
            """
            SELECT first_name, last_name
            FROM techs
            WHERE active = TRUE
              AND status = 'Active'
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                            )
            """,
                        (current_shop_uuid, current_shop_id, domain),
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            GROUP BY repair_type, tech_id, tech_name, COALESCE(is_pending, FALSE)
            ORDER BY tech_name NULLS FIRST, repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND ro = %s
                  AND tech_name IS NULL
                  AND COALESCE(is_pending, FALSE) = FALSE
                  AND repair_type = %s
                ORDER BY line_number
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value, filter_type),
            )
        elif mode_value == "pending":
            cur.execute(
                """
                SELECT repair_type, line_key, line_number, description, hours
                FROM ro_line_assignments
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND ro = %s
                  AND tech_name IS NULL
                  AND COALESCE(is_pending, FALSE) = TRUE
                ORDER BY repair_type, line_number
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value),
            )
        else:
            filter_type = _normalize_repair_type(repair_type)
            selected_tech = (tech_name or "").strip()
            cur.execute(
                """
                SELECT repair_type, line_key, line_number, description, hours
                FROM ro_line_assignments
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND ro = %s
                  AND tech_name = %s
                  AND repair_type = %s
                ORDER BY line_number
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value, selected_tech, filter_type),
            )

        line_rows = cur.fetchall()

        cur.execute(
            """
            SELECT id, first_name, last_name, pay_rate
            FROM techs
            WHERE active = TRUE
              AND status = 'Active'
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                            )
            ORDER BY first_name, last_name
            """,
                        (current_shop_uuid, current_shop_id, domain),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                                    )
                """,
                                (target_tech_id, current_shop_uuid, current_shop_id, domain),
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
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                                    )
                  AND TRIM(CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) = %s
                LIMIT 1
                """,
                                (current_shop_uuid, current_shop_id, domain, target_tech_name),
            )
            active_named = cur.fetchone()
            if not active_named:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})

        selected_keys = set()
        manual_lines = []
        for item in selected_lines:
            if not isinstance(item, dict):
                continue
            repair_type = _normalize_repair_type(item.get("repair_type") or target_type)
            line_key = str(item.get("line_key") or "")
            is_manual = bool(item.get("is_manual"))

            if is_manual:
                description = (item.get("description") or "").strip()
                hours_value = _parse_float_value(item.get("hours"))
                if not description:
                    return JSONResponse(status_code=400, content={"error": "Manual line description is required"})
                if hours_value < 0:
                    return JSONResponse(status_code=400, content={"error": "Manual line hours cannot be negative"})
                manual_lines.append(
                    {
                        "repair_type": repair_type,
                        "description": description,
                        "hours": hours_value,
                    }
                )
                continue

            if not line_key:
                continue
            selected_keys.add((repair_type, line_key))

        scope_rows = _get_scope_rows(
            cur,
            domain,
            ro_value,
            source,
            shop_id=current_shop_id,
            shop_uuid=current_shop_uuid,
        )
        scope_keys = {
            (str(row.get("repair_type") or ""), str(row.get("line_key") or "")): int(row.get("id"))
            for row in scope_rows
        }

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

        manual_insert_count = 0
        if manual_lines:
            cur.execute(
                """
                SELECT line_key
                FROM ro_line_assignments
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND ro = %s
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value),
            )
            existing_line_keys = {str(row.get("line_key") or "") for row in (cur.fetchall() or [])}
            base_stamp = int(datetime.utcnow().timestamp())

            for index, manual_line in enumerate(manual_lines, start=1):
                base_key = f"manual-{base_stamp}-{index}"
                next_key = base_key
                suffix = 1
                while next_key in existing_line_keys:
                    suffix += 1
                    next_key = f"{base_key}-{suffix}"
                existing_line_keys.add(next_key)

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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, %s, %s::uuid)
                    """,
                    (
                        ro_value,
                        manual_line["repair_type"],
                        manual_line["repair_type"],
                        next_key,
                        f"M{index}",
                        manual_line["description"],
                        manual_line["hours"],
                        target_tech_id,
                        target_tech_name or None,
                        domain,
                        current_shop_id,
                        current_shop_uuid,
                    ),
                )
                manual_insert_count += 1

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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

        if selected_ids or manual_insert_count > 0:
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



@router.post("/ro-assignment-unassign")
async def unassign_ro_assignment_lines(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    selected_sources = data.get("selected_sources") or []

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})
    if not isinstance(selected_sources, list) or not selected_sources:
        return JSONResponse(status_code=400, content={"error": "selected_sources is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        before_rows = cur.fetchall() or []
        before_by_type = {
            _normalize_repair_type(row.get("repair_type")): _parse_float_value(row.get("total_hours"))
            for row in before_rows
        }
        before_total_assigned = sum(before_by_type.values())

        target_ids = set()
        touched_tech_labels = set()
        for source in selected_sources:
            if not isinstance(source, dict):
                continue
            source_mode = (source.get("mode") or "").strip().lower()
            if source_mode not in {"tech", "pending", "unassigned"}:
                continue

            rows = _get_scope_rows(
                cur,
                domain,
                ro_value,
                source,
                shop_id=current_shop_id,
                shop_uuid=current_shop_uuid,
            )
            for row in rows:
                row_id = row.get("id")
                if row_id is None:
                    continue
                target_ids.add(int(row_id))

            if source_mode == "tech":
                tech_label = (source.get("tech_name") or "").strip()
                if tech_label:
                    touched_tech_labels.add(tech_label)

        if target_ids:
            cur.execute(
                """
                UPDATE ro_line_assignments
                SET tech_id = NULL,
                    tech_name = NULL,
                    is_pending = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                """,
                (list(target_ids),),
            )

        cur.execute(
            """
            SELECT repair_type, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_name IS NOT NULL
            GROUP BY repair_type
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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

        if target_ids:
            if touched_tech_labels:
                label = ", ".join(sorted(touched_tech_labels))
                detail = f"Tech unassigned → {label}"
            else:
                detail = "Selected repair lines reset to unassigned"
            _log_ro_activity(cur, domain, ro_value, "tech_assignment", detail)

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
        return {
            "status": "ok",
            "updated_count": len(target_ids),
        }
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

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
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                                    )
                """,
                                (tech_id, current_shop_uuid, current_shop_id, domain),
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
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND (domain = %s OR domain IS NULL))
                                    )
                  AND TRIM(CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) = %s
                LIMIT 1
                """,
                                (current_shop_uuid, current_shop_id, domain, tech_name),
            )
            active_named = cur.fetchone()
            if not active_named:
                return JSONResponse(status_code=400, content={"error": "Selected tech is archived or unavailable"})

        cur.execute(
            """
            INSERT INTO ro_assignments (ro, role, tech_id, tech_name, excluded_lines, assigned_hours, domain, shop_id, shop_uuid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
            ON CONFLICT (ro, role, domain)
            DO UPDATE SET
                tech_id = EXCLUDED.tech_id,
                tech_name = EXCLUDED.tech_name,
                excluded_lines = EXCLUDED.excluded_lines,
                assigned_hours = EXCLUDED.assigned_hours,
                shop_id = EXCLUDED.shop_id,
                shop_uuid = EXCLUDED.shop_uuid,
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
                current_shop_id,
                current_shop_uuid,
            ),
        )
        conn.commit()
        return {"status": "ok"}
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

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
                                                 AND (
                                                                t.shop_uuid = %s::uuid
                                                         OR (t.shop_uuid IS NULL AND t.shop_id = %s AND (t.domain = %s OR t.domain IS NULL))
                                                 )
                        WHERE (
                                        f.shop_uuid = %s::uuid
                                 OR (f.shop_uuid IS NULL AND f.shop_id = %s AND f.domain = %s)
                                    )
              AND f.status = 'ready_to_flag'
            GROUP BY f.tech_id
            ORDER BY COALESCE(MAX(NULLIF(TRIM(f.tech_name), '')), CONCAT('Tech #', f.tech_id::text))
            """,
                        (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain),
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
                WHERE (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                      )
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
                        WHERE (
                                        f.shop_uuid = %s::uuid
                                 OR (f.shop_uuid IS NULL AND f.shop_id = %s AND f.domain = %s)
                                    )
              AND f.status = 'ready_to_flag'
            GROUP BY f.tech_id, f.ro
            ORDER BY f.tech_id, f.ro
            """,
                        (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

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
                    WHERE (
                            shop_uuid = %s::uuid
                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                          )
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
                                WHERE (
                                                f.shop_uuid = %s::uuid
                                         OR (f.shop_uuid IS NULL AND f.shop_id = %s AND f.domain = %s)
                                            )
                  AND f.status = 'ready_to_flag'
                  AND f.tech_id = %s
                  AND f.ro = ANY(%s)
                GROUP BY f.tech_id, f.ro
                ORDER BY f.ro
                """,
                                (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain, tech_id, ro_values),
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
                WHERE (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                      )
                  AND status = 'ready_to_flag'
                  AND tech_id = %s
                  AND ro = ANY(%s)
                """,
                (current_shop_uuid, current_shop_id, domain, tech_id, ro_values),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT phase
            FROM ro_phases
                        WHERE ro = %s
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            """,
                        (ro, current_shop_uuid, current_shop_id, domain),
        )
        prev_row = cur.fetchone() or {}
        previous_phase = (prev_row.get("phase") or "").strip().lower()

        cur.execute(
            """
            INSERT INTO ro_phases (ro, phase, domain, shop_id, shop_uuid)
            VALUES (%s, %s, %s, %s, %s::uuid)
            ON CONFLICT (ro, domain)
            DO UPDATE SET phase = EXCLUDED.phase,
                          shop_id = EXCLUDED.shop_id,
                          shop_uuid = EXCLUDED.shop_uuid,
                          updated_at = CURRENT_TIMESTAMP
            """,
            (ro, phase, domain, current_shop_id, current_shop_uuid),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                   year,
                   make,
                   model,
                 estimator,
                 written_by,
                   labor_repairs,
                   paint_repairs
            FROM saved_estimates
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
            """,
                        (current_shop_uuid, current_shop_id, domain),
        )
        estimate_rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, phase
            FROM ro_phases
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            """,
            (current_shop_uuid, current_shop_id, domain),
        )
        phase_rows = cur.fetchall()
        phase_map = {row.get("ro"): row.get("phase") for row in phase_rows}
        closed_phase_keys = {"complete", "complete/finish"}

        for row in estimate_rows:
            ro_value = (row.get("ro") or "").strip()
            if ro_value:
                _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT ro, repair_type, tech_name, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            GROUP BY ro, repair_type, tech_name
            """,
            (current_shop_uuid, current_shop_id, domain),
        )
        assignment_rows = cur.fetchall()
        tech_map = {}
        for assignment in assignment_rows:
            ro_value = (assignment.get("ro") or "").strip()
            if not ro_value:
                continue
            current = tech_map.setdefault(ro_value, {"labor_tech": "", "paint_tech": ""})
            repair_type = _normalize_repair_type(assignment.get("repair_type"))
            tech_name = (assignment.get("tech_name") or "").strip()
            if not tech_name:
                continue
            if repair_type == "body" and not current["labor_tech"]:
                current["labor_tech"] = tech_name
            elif repair_type == "paint" and not current["paint_tech"]:
                current["paint_tech"] = tech_name

        items = []
        for row in estimate_rows:
            ro = row.get("ro")
            phase_value = str(phase_map.get(ro, "teardown") or "teardown").strip().lower()
            if phase_value in closed_phase_keys:
                continue
            labor_repairs = _parse_json_field(row.get("labor_repairs"))
            paint_repairs = _parse_json_field(row.get("paint_repairs"))

            labor_hours = _sum_hours(labor_repairs)
            paint_hours = _sum_hours(paint_repairs)

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            short_vehicle = " ".join(part for part in (year, make, model) if part)
            vehicle_display = short_vehicle or row.get("vehicle") or ""
            estimator_display = (row.get("estimator") or "").strip() or (row.get("written_by") or "").strip()
            ro_tech = tech_map.get(str(ro or "").strip(), {})
            labor_tech = (ro_tech.get("labor_tech") or "").strip() or "Unassigned"
            paint_tech = (ro_tech.get("paint_tech") or "").strip() or "Unassigned"

            items.append(
                {
                    "ro": ro,
                    "vehicle": vehicle_display,
                    "phase": phase_value,
                    "estimator": estimator_display,
                    "labor_tech": labor_tech,
                    "labor_hours": labor_hours,
                    "paint_tech": paint_tech,
                    "paint_hours": paint_hours,
                }
            )

        return {"items": items}
    finally:
        cur.close()



@router.get("/ro-notes")
async def list_ro_notes(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "notes": []})
    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "notes": []})
        cur.execute(
            """
            SELECT note, created_at, created_by
            FROM ro_notes
            WHERE ro = %s
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            ORDER BY created_at DESC
            """,
            (ro, current_shop_uuid, current_shop_id, domain),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            ORDER BY saved_at ASC, id ASC
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            ORDER BY created_at DESC, id DESC
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND paid_at IS NOT NULL
            GROUP BY COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned'), paid_at
            ORDER BY paid_at DESC
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    data = await request.json()
    ro = (data.get("ro") or "").strip()
    note = (data.get("note") or "").strip()
    if not ro or not note:
        return JSONResponse(status_code=400, content={"error": "ro and note are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        created_by = _resolve_request_user_display_name(request, cur, domain)
        cur.execute(
            """
            INSERT INTO ro_notes (ro, note, domain, shop_id, shop_uuid, created_by)
            VALUES (%s, %s, %s, %s, %s::uuid, %s)
            """,
            (ro, note, domain, current_shop_id, current_shop_uuid, created_by),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "ros": []})

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                                     estimator,
                                     written_by,
                   parts_repairs,
                   saved_at
            FROM saved_estimates
            WHERE shop_uuid = %s::uuid
              AND ro IS NOT NULL
              AND ro <> ''
            ORDER BY ro, saved_at DESC, id DESC
            """,
                        (current_shop_uuid,),
        )
        rows = cur.fetchall()

        cur.execute(
            """
            SELECT ro, phase
            FROM ro_phases
            WHERE shop_uuid = %s::uuid
            """,
            (current_shop_uuid,),
        )
        phase_rows = cur.fetchall() or []
        phase_map = {str(row.get("ro") or "").strip(): str(row.get("phase") or "").strip().lower() for row in phase_rows}
        closed_phase_keys = {"complete", "complete/finish"}

        cur.execute(
            """
            SELECT ro, arrival_date, ordered_lines, arrived_count, returned_count, created_at
            FROM parts_orders
            WHERE shop_uuid = %s::uuid
            ORDER BY created_at DESC
            """,
            (current_shop_uuid,),
        )
        orders = cur.fetchall()

        cur.execute(
            """
            SELECT ro, COUNT(*) as arrived
            FROM parts_received
            WHERE shop_uuid = %s::uuid
            GROUP BY ro
            """,
            (current_shop_uuid,),
        )
        received_rows = cur.fetchall()
        received_map = {row["ro"]: int(row.get("arrived") or 0) for row in received_rows}

        cur.execute(
            """
            SELECT ro, line_id
            FROM parts_received
            WHERE shop_uuid = %s::uuid
              AND COALESCE(returned, FALSE) = FALSE
            """,
                        (current_shop_uuid,),
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
            WHERE shop_uuid = %s::uuid
              AND COALESCE(returned, FALSE) = TRUE
            GROUP BY ro
            """,
                        (current_shop_uuid,),
        )
        returned_rows = cur.fetchall() or []
        returned_map = {row["ro"]: int(row.get("returned") or 0) for row in returned_rows}

        cur.execute(
            """
            SELECT
                rla.ro,
                rla.repair_type,
                COALESCE(
                    NULLIF(TRIM(rla.tech_name), ''),
                    NULLIF(TRIM(CONCAT(COALESCE(t.first_name, ''), ' ', COALESCE(t.last_name, ''))), '')
                ) AS tech_name
            FROM ro_line_assignments rla
            LEFT JOIN techs t
              ON t.id = rla.tech_id
              AND t.shop_uuid = %s::uuid
            WHERE rla.shop_uuid = %s::uuid
              AND rla.ro IS NOT NULL
              AND rla.ro <> ''
            ORDER BY rla.ro, CASE WHEN rla.repair_type = 'body' THEN 0 WHEN rla.repair_type = 'paint' THEN 1 ELSE 2 END
            """,
            (
                current_shop_uuid,
                current_shop_uuid,
            ),
        )
        tech_rows = cur.fetchall() or []
        tech_by_ro = {}
        for tech_row in tech_rows:
            ro_key = str(tech_row.get("ro") or "").strip()
            if not ro_key or ro_key in tech_by_ro:
                continue
            tech_name = (tech_row.get("tech_name") or "").strip()
            if not tech_name:
                continue
            tech_by_ro[ro_key] = tech_name

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
            ro_key = str(ro or "").strip()
            phase_value = phase_map.get(str(ro or "").strip(), "")
            if phase_value in closed_phase_keys:
                continue
            parts_repairs = _parse_json_field(row.get("parts_repairs"))
            if not isinstance(parts_repairs, list):
                parts_repairs = []

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

            estimator_name = (row.get("estimator") or "").strip() or (row.get("written_by") or "").strip()

            summary = order_summary.get(ro, {})
            ordered_ids = summary.get("ordered_ids", set())
            returned_count = returned_map.get(ro, 0)
            on_order = max(0, len(ordered_ids) - returned_count)
            ros.append(
                {
                    "ro": ro,
                    "vehicle": row.get("vehicle"),
                    "estimator": estimator_name or "—",
                    "tech": tech_by_ro.get(ro_key, "—"),
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
    """
    ⚠️ DEPRECATED: Use GET /parts/ro/{ro}/full instead.
    This endpoint returns only the parts lines. The new endpoint consolidates
    all parts data (lines, on-order, arrived, returned) in a single request.
    """
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "lines": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "lines": []})

        cur.execute(
            """
            SELECT ordered_lines
            FROM parts_orders
            WHERE shop_uuid = %s::uuid AND ro = %s
            """,
            (current_shop_uuid, ro),
        )
        order_rows = cur.fetchall() or []
        ordered_ids = set()
        for order_row in order_rows:
            ordered_ids.update(_normalize_line_ids(order_row.get("ordered_lines") or []))

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE shop_uuid = %s::uuid AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (current_shop_uuid, ro),
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
            WHERE shop_uuid = %s::uuid AND ro = %s AND COALESCE(returned, FALSE) = TRUE
            """,
            (current_shop_uuid, ro),
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
            WHERE shop_uuid = %s::uuid AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, ro),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT ordered_lines
            FROM parts_orders
            WHERE shop_uuid = %s::uuid AND ro = %s
            """,
            (current_shop_uuid, ro),
        )
        existing_orders = cur.fetchall() or []
        already_ordered = set()
        for existing_order in existing_orders:
            already_ordered.update(_normalize_line_ids(existing_order.get("ordered_lines") or []))

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE shop_uuid = %s::uuid AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (current_shop_uuid, ro),
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
            WHERE shop_uuid = %s::uuid AND ro = %s AND COALESCE(returned, FALSE) = TRUE
            """,
            (current_shop_uuid, ro),
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
            cur.execute(
                """
                SELECT name
                FROM parts_vendors
                WHERE id = %s
                  AND (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
                """,
                (vendor_id, current_shop_uuid, current_shop_id, domain),
            )
            row = cur.fetchone()
            vendor_name = row["name"] if row else None

        cur.execute(
            """
            INSERT INTO parts_orders
            (ro, vendor_id, vendor_name, arrival_date, ordered_lines, domain, shop_id, shop_uuid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::uuid)
            """,
            (
                ro,
                vendor_id,
                vendor_name,
                arrival_date,
                json.dumps(sorted(ordered_lines)),
                domain,
                current_shop_id,
                current_shop_uuid,
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "items": []})
        cur.execute(
            """
            SELECT line_id, vendor, part_number, list_price, cost, eta, invoice_number, invoice_total,
                   returned, received_business_date, received_at
            FROM parts_received
            WHERE shop_uuid = %s::uuid AND ro = %s
            ORDER BY COALESCE(received_business_date, received_at::date) DESC, received_at DESC
            """,
                        (current_shop_uuid, ro),
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
                "received_date": (
                    row.get("received_business_date").isoformat()
                    if row.get("received_business_date")
                    else (row.get("received_at").date().isoformat() if row.get("received_at") else None)
                ),
                "received_at": row.get("received_at"),
            }
            for row in rows
        ]
        return {"items": items}
    finally:
        cur.close()



@router.get("/parts/arrived-lines")
async def list_arrived_lines(request: Request, ro: str):
    """
    ⚠️ DEPRECATED: Use GET /parts/ro/{ro}/full instead.
    This endpoint returns only arrived parts. The new endpoint consolidates
    all parts data (lines, on-order, arrived, returned) in a single request.
    """
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "items": []})

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
            ) AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
                                                SELECT line_id, vendor, description, part_number, list_price, cost, invoice_number, received_business_date, received_at
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                        )
              AND ro = %s
              AND COALESCE(returned, FALSE) = FALSE
                        ORDER BY COALESCE(received_business_date, received_at::date) DESC, line_id
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                    "description": row.get("description") or metadata.get("description") or "",
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        updated_count = 0
        for line_id in line_ids:
            cur.execute(
                """
                UPDATE parts_received
                                SET returned = TRUE,
                                                                                returned_at = CURRENT_TIMESTAMP,
                                                                                returned_business_date = COALESCE(%s, CURRENT_DATE)
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                )
                  AND ro = %s
                  AND line_id = %s
                  AND COALESCE(returned, FALSE) = FALSE
                """,
                                                                (local_business_date, current_shop_uuid, current_shop_id, domain, ro_value, line_id),
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
                            AND (parts_orders.shop_uuid = %s::uuid OR (parts_orders.shop_uuid IS NULL AND parts_orders.shop_id = %s))
              AND parts_orders.ro = %s
            """,
                        (domain, current_shop_uuid, current_shop_id, ro_value),
        )

        conn.commit()
        return {"status": "ok", "returned_count": updated_count}
    finally:
        cur.close()



@router.get("/parts/returned-lines")
async def list_returned_lines(request: Request, ro: str):
    """
    ⚠️ DEPRECATED: Use GET /parts/ro/{ro}/full instead.
    This endpoint returns only returned parts. The new endpoint consolidates
    all parts data (lines, on-order, arrived, returned) in a single request.
    """
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "items": []})

        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
            ) AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
                        SELECT line_id, vendor, description, part_number, cost, returned_business_date, returned_at, received_business_date, received_at
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                        )
              AND ro = %s
              AND COALESCE(returned, FALSE) = TRUE
                        ORDER BY COALESCE(returned_business_date, returned_at::date, received_business_date, received_at::date) DESC, line_id
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
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
                    "description": row.get("description") or metadata.get("description") or "",
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
    """
    ⚠️ DEPRECATED: Use GET /parts/ro/{ro}/full instead.
    This endpoint returns only on-order parts. The new endpoint consolidates
    all parts data (lines, on-order, arrived, returned) in a single request.
    """
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "items": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required", "items": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "items": []})

        cur.execute(
            """
            SELECT line_id
            FROM parts_received
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
            ) AND ro = %s AND COALESCE(returned, FALSE) = FALSE
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
            ) AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
            ) AND ro = %s
            ORDER BY created_at DESC, id DESC
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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



@router.get("/parts/ro/{ro}/full")
async def get_parts_ro_full(request: Request, ro: str):
    """
    Consolidated parts data endpoint for a single RO.
    Groups all parts data server-side into vendors, on_order, arrived, and returned categories.
    """
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "RO is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        # Fetch base parts from estimate
        cur.execute(
            """
            SELECT parts_repairs
            FROM saved_estimates
            WHERE shop_uuid = %s::uuid AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, ro_value),
        )
        estimate_row = cur.fetchone()
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs")) if estimate_row else []
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        # Build line metadata from estimate
        line_metadata = {}
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
            line_metadata[idx] = {
                "line": item.get("line") or idx,
                "description": parsed_description,
                "part_number": part_number,
                "part_type": item.get("part_type"),
                "price": float(item.get("price") or 0),
                "qty": float(item.get("qty") or 0),
            }

        # Fetch parts orders
        cur.execute(
            """
            SELECT id, vendor_name, arrival_date, ordered_lines
            FROM parts_orders
            WHERE shop_uuid = %s::uuid AND ro = %s
            ORDER BY created_at DESC, id DESC
            """,
            (current_shop_uuid, ro_value),
        )
        order_rows = cur.fetchall() or []

        # Fetch received parts
        cur.execute(
            """
            SELECT line_id, vendor, description, part_number, list_price, cost, invoice_number, received_business_date, received_at, returned, returned_business_date, returned_at
            FROM parts_received
            WHERE shop_uuid = %s::uuid AND ro = %s
            ORDER BY COALESCE(received_business_date, received_at::date) DESC, line_id
            """,
            (current_shop_uuid, ro_value),
        )
        received_rows = cur.fetchall() or []

        # Build received maps
        received_by_line = {}
        received_not_returned_ids = set()
        returned_ids = set()

        for row in received_rows:
            line_id = int(row.get("line_id") or 0)
            is_returned = row.get("returned") or False

            received_by_line[line_id] = row

            if is_returned:
                returned_ids.add(line_id)
            else:
                received_not_returned_ids.add(line_id)

        # Build ordered and included line IDs
        ordered_ids = set()
        included_line_ids = set()
        for order_row in order_rows:
            ordered_ids.update(_normalize_line_ids(order_row.get("ordered_lines") or []))

        # Prepare grouped data
        all_lines = []
        vendors_dict = {}
        on_order_items = []
        arrived_items = []
        returned_items = []

        # Process all lines with status
        for line_id in sorted(line_metadata.keys()):
            metadata = line_metadata[line_id]
            received_row = received_by_line.get(line_id)

            line_obj = {
                "id": line_id,
                "line": metadata.get("line"),
                "description": metadata.get("description"),
                "part_number": metadata.get("part_number"),
                "part_type": metadata.get("part_type"),
                "price": metadata.get("price"),
                "qty": metadata.get("qty"),
                "status": "available",  # default
            }

            # Determine status
            if line_id in returned_ids:
                line_obj["status"] = "returned"
            elif line_id in received_not_returned_ids:
                line_obj["status"] = "arrived"
            elif line_id in ordered_ids:
                line_obj["status"] = "on_order"

            all_lines.append(line_obj)

        # Process on-order items
        for order_row in order_rows:
            order_id = order_row.get("id")
            vendor_name = order_row.get("vendor_name") or ""
            arrival_date = order_row.get("arrival_date")
            ordered_line_ids = _normalize_line_ids(order_row.get("ordered_lines") or [])

            for line_id in sorted(ordered_line_ids):
                if line_id in received_not_returned_ids or line_id in included_line_ids:
                    continue
                metadata = line_metadata.get(line_id, {})
                on_order_items.append(
                    {
                        "order_id": order_id,
                        "line_id": line_id,
                        "line": metadata.get("line") or line_id,
                        "description": metadata.get("description") or "",
                        "part_number": metadata.get("part_number") or "",
                        "qty": metadata.get("qty") or 0,
                        "list": metadata.get("price") or 0,
                        "vendor": vendor_name,
                        "eta": arrival_date.isoformat() if arrival_date else None,
                    }
                )
                included_line_ids.add(line_id)
                # Track vendor
                if vendor_name not in vendors_dict:
                    vendors_dict[vendor_name] = {"name": vendor_name, "count": 0}
                vendors_dict[vendor_name]["count"] += 1

        # Process arrived items
        for line_id in sorted(received_not_returned_ids):
            row = received_by_line.get(line_id, {})
            metadata = line_metadata.get(line_id, {})
            arrived_items.append(
                {
                    "line_id": line_id,
                    "line": metadata.get("line") or line_id,
                    "description": row.get("description") or metadata.get("description") or "",
                    "part_number": row.get("part_number") or metadata.get("part_number") or "",
                    "list": float(row.get("list_price") or metadata.get("price") or 0),
                    "vendor": row.get("vendor") or "",
                    "cost": float(row.get("cost") or 0),
                    "invoice_number": row.get("invoice_number") or "",
                    "arrived_date": (
                        row.get("received_business_date").isoformat() if row.get("received_business_date")
                        else (row.get("received_at").date().isoformat() if row.get("received_at") else None)
                    ),
                }
            )
            if row.get("vendor"):
                if row.get("vendor") not in vendors_dict:
                    vendors_dict[row.get("vendor")] = {"name": row.get("vendor"), "count": 0}
                vendors_dict[row.get("vendor")]["count"] += 1

        # Process returned items
        for line_id in sorted(returned_ids):
            row = received_by_line.get(line_id, {})
            metadata = line_metadata.get(line_id, {})
            return_date_value = (
                row.get("returned_business_date")
                or (row.get("returned_at").date() if row.get("returned_at") else None)
            )
            returned_items.append(
                {
                    "line_id": line_id,
                    "line": metadata.get("line") or line_id,
                    "description": row.get("description") or metadata.get("description") or "",
                    "part_number": row.get("part_number") or metadata.get("part_number") or "",
                    "vendor": row.get("vendor") or "",
                    "cost": float(row.get("cost") or 0),
                    "return_date": return_date_value.isoformat() if return_date_value else None,
                }
            )

        return {
            "ro": ro_value,
            "all_lines": all_lines,
            "vendors": list(vendors_dict.values()),
            "on_order": on_order_items,
            "arrived": arrived_items,
            "returned": returned_items,
        }
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
    manual_items = data.get("manual_items") or []

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
    if not isinstance(items, list):
        return JSONResponse(status_code=400, content={"error": "Selected items data is invalid"})
    if manual_items is not None and not isinstance(manual_items, list):
        return JSONResponse(status_code=400, content={"error": "Manual items data is invalid"})
    if len(items) == 0 and len(manual_items or []) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Select at least one part or add at least one manual part"},
        )

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

    normalized_manual_items = []
    if manual_items:
        for manual_item in manual_items:
            if not isinstance(manual_item, dict):
                return JSONResponse(status_code=400, content={"error": "Manual item data is invalid"})

            description = str(manual_item.get("description") or "").strip()
            part_number = str(manual_item.get("part_number") or "").strip()
            vendor = str(manual_item.get("vendor") or vendor_name_input).strip()

            try:
                qty_received = float(manual_item.get("qty_received"))
                cost = float(manual_item.get("cost"))
            except (TypeError, ValueError):
                return JSONResponse(status_code=400, content={"error": "Manual item values are invalid"})

            if not description:
                return JSONResponse(status_code=400, content={"error": "Manual item description is required"})
            if qty_received <= 0:
                return JSONResponse(status_code=400, content={"error": "Manual item quantity must be greater than zero"})
            if cost < 0:
                return JSONResponse(status_code=400, content={"error": "Manual item cost cannot be negative"})
            if not vendor:
                return JSONResponse(status_code=400, content={"error": "Vendor is required for manual items"})

            selected_cost_total += cost
            normalized_manual_items.append(
                {
                    "description": description,
                    "part_number": part_number,
                    "qty_received": qty_received,
                    "cost": cost,
                    "vendor": vendor,
                }
            )

    if round(selected_cost_total, 2) != round(invoice_total, 2):
        return JSONResponse(status_code=400, content={"error": "Selected part costs must equal total invoice amount"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        line_ids_by_order = {}
        for item in normalized_items:
            order_id = item["order_id"]
            line_ids_by_order.setdefault(order_id, set()).add(item["line_id"])

        for order_id, selected_line_ids in line_ids_by_order.items():
            cur.execute(
                """
                SELECT ordered_lines
                FROM parts_orders
                                WHERE id = %s
                                    AND ro = %s
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
                LIMIT 1
                """,
                                (order_id, ro_value, current_shop_uuid, current_shop_id, domain),
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
                    (ro, line_id, vendor, description, part_number, qty_received, list_price, cost, eta, invoice_number, invoice_total, returned, received_business_date, domain, shop_id, shop_uuid)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, COALESCE(%s, CURRENT_DATE), %s, %s, %s::uuid)
                ON CONFLICT (ro, line_id, domain)
                DO UPDATE SET
                    vendor = EXCLUDED.vendor,
                    description = EXCLUDED.description,
                    part_number = EXCLUDED.part_number,
                    qty_received = EXCLUDED.qty_received,
                    list_price = EXCLUDED.list_price,
                    cost = EXCLUDED.cost,
                    eta = EXCLUDED.eta,
                    invoice_number = EXCLUDED.invoice_number,
                    invoice_total = EXCLUDED.invoice_total,
                    returned = FALSE,
                    received_business_date = EXCLUDED.received_business_date,
                    shop_id = EXCLUDED.shop_id,
                    shop_uuid = EXCLUDED.shop_uuid,
                    received_at = CURRENT_TIMESTAMP
                """,
                (
                    ro_value,
                    item["line_id"],
                    item["vendor"],
                    None,
                    item["part_number"] or None,
                    item["qty_received"],
                    item["list_price"],
                    item["cost"],
                    item["eta"],
                    invoice_number,
                    invoice_total,
                    local_business_date,
                    domain,
                    current_shop_id,
                    current_shop_uuid,
                ),
            )

        if normalized_manual_items:
            cur.execute(
                """
                SELECT COALESCE(MIN(line_id), 0) AS min_line_id
                FROM parts_received
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                )
                  AND ro = %s
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value),
            )
            min_line_row = cur.fetchone() or {}
            min_line_id = int(min_line_row.get("min_line_id") or 0)
            next_manual_line_id = min_line_id - 1 if min_line_id <= 0 else -1

            for manual_item in normalized_manual_items:
                cur.execute(
                    """
                    INSERT INTO parts_received
                        (ro, line_id, vendor, description, part_number, qty_received, list_price, cost, eta, invoice_number, invoice_total, returned, received_business_date, domain, shop_id, shop_uuid)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, NULL, %s, NULL, %s, %s, FALSE, COALESCE(%s, CURRENT_DATE), %s, %s, %s::uuid)
                    """,
                    (
                        ro_value,
                        next_manual_line_id,
                        manual_item["vendor"],
                        manual_item["description"],
                        manual_item["part_number"] or None,
                        manual_item["qty_received"],
                        manual_item["cost"],
                        invoice_number,
                        invoice_total,
                        local_business_date,
                        domain,
                        current_shop_id,
                        current_shop_uuid,
                    ),
                )
                next_manual_line_id -= 1

        for order_id, selected_line_ids in line_ids_by_order.items():
            cur.execute(
                """
                SELECT ordered_lines
                FROM parts_orders
                                WHERE id = %s
                                    AND ro = %s
                                    AND (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
                LIMIT 1
                """,
                                (order_id, ro_value, current_shop_uuid, current_shop_id, domain),
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
                            AND (parts_orders.shop_uuid = %s::uuid OR (parts_orders.shop_uuid IS NULL AND parts_orders.shop_id = %s))
              AND parts_orders.ro = %s
            """,
                        (domain, current_shop_uuid, current_shop_id, ro_value),
        )

        conn.commit()
        return {"status": "ok"}
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            """
            DELETE FROM parts_received
            WHERE ro = %s
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
            """,
            (ro, current_shop_uuid, current_shop_id, domain),
        )

        for item in items:
            line_id = item.get("line_id")
            vendor = (item.get("vendor") or "").strip()
            cost = item.get("cost")
            returned = bool(item.get("returned"))
            if not line_id or not vendor:
                continue
            cur.execute(
                """
                INSERT INTO parts_received (ro, line_id, vendor, cost, returned, domain, shop_id, shop_uuid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                (ro, line_id, vendor, cost, returned, domain, current_shop_id, current_shop_uuid),
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
                            AND (parts_orders.shop_uuid = %s::uuid OR (parts_orders.shop_uuid IS NULL AND parts_orders.shop_id = %s))
              AND parts_orders.ro = %s
            """,
                        (domain, current_shop_uuid, current_shop_id, ro),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        # Get assignments with tech info
        cur.execute(
            """
            SELECT a.ro, a.role, a.tech_id, a.tech_name, a.excluded_lines, a.assigned_hours,
                   t.hourly_rate as tech_rate
            FROM ro_assignments a
            LEFT JOIN techs t ON a.tech_id = t.id
            WHERE (
                    a.shop_uuid = %s::uuid
                 OR (a.shop_uuid IS NULL AND a.shop_id = %s AND a.domain = %s)
                  )
              AND a.ro = %s
            """,
            (current_shop_uuid, current_shop_id, domain, ro),
        )
        assignment_rows = cur.fetchall()

        if not assignment_rows:
            return {"assignments": []}

        # Get the estimate data to calculate actual hours
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
            (current_shop_uuid, current_shop_id, domain, ro),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        # Get the assignment
        cur.execute(
            """
            SELECT excluded_lines
            FROM ro_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s AND tech_id = %s AND role = %s
            """,
            (current_shop_uuid, current_shop_id, domain, ro, tech_id, role),
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})

        saved_snapshot = _parse_json_field(row.get("estimate_snapshot"))
        if isinstance(saved_snapshot, dict) and saved_snapshot:
            saved_snapshot["unified_lines"] = _build_unified_estimate_lines(saved_snapshot)
            return {"estimate": saved_snapshot}

        labor_repairs = _parse_json_field(row.get("labor_repairs"))
        paint_repairs = _parse_json_field(row.get("paint_repairs"))
        parts_repairs = _parse_json_field(row.get("parts_repairs"))
        totals = _parse_json_field(row.get("estimate_totals"))

        if not isinstance(labor_repairs, list):
            labor_repairs = []
        if not isinstance(paint_repairs, list):
            paint_repairs = []
        if not isinstance(parts_repairs, list):
            parts_repairs = []
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY repair_type, line_number
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        line_assignments = cur.fetchall()
        
        # Get tech assignments from grouped line assignments (like dashboard does)
        cur.execute(
            """
            SELECT repair_type, tech_name, COALESCE(SUM(hours), 0) AS total_hours
            FROM ro_line_assignments
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            GROUP BY repair_type, tech_name
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
            ORDER BY created_at DESC
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
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






