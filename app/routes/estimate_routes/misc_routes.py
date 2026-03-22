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

@router.patch("/ro-dates")
async def update_ro_dates(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = (data.get("ro") or "").strip()
    field = (data.get("field") or "").strip().lower()
    value = (data.get("value") or "").strip()

    if not ro_value or field not in {"in_date", "ecd_date", "picked_up"} or not value:
        return JSONResponse(status_code=400, content={"error": "ro, field, and value are required"})

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "value must be YYYY-MM-DD"})

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
            SELECT id, in_date, ecd_date, picked_up
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

        old_in_date = _coerce_date(row.get("in_date"))
        old_ecd_date = _coerce_date(row.get("ecd_date"))
        old_picked_up = _coerce_date(row.get("picked_up"))

        if field == "in_date":
            cur.execute(
                """
                UPDATE saved_estimates
                SET in_date = %s
                WHERE id = %s
                """,
                (parsed_date, row.get("id")),
            )
        elif field == "ecd_date":
            cur.execute(
                """
                UPDATE saved_estimates
                SET ecd_date = %s
                WHERE id = %s
                """,
                (parsed_date, row.get("id")),
            )
        else:
            cur.execute(
                """
                UPDATE saved_estimates
                SET picked_up = %s
                WHERE id = %s
                """,
                (parsed_date, row.get("id")),
            )

        old_value = old_in_date if field == "in_date" else (old_ecd_date if field == "ecd_date" else old_picked_up)
        if old_value != parsed_date:
            label = "In-date" if field == "in_date" else ("ECD" if field == "ecd_date" else "Picked Up")
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





