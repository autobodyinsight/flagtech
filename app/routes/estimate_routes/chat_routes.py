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

@router.post("/chat/send")
async def chat_send(request: Request):
    domain = str(get_user_domain(request) or "").strip().lower()
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    try:
        recipient_user_id = int(data.get("to_user_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "to_user_id is required"})

    kind = str(data.get("kind") or "message").strip().lower()
    if kind not in {"message", "task"}:
        return JSONResponse(status_code=400, content={"error": "kind must be message or task"})

    body = str(data.get("text") or "").strip()
    if not body:
        return JSONResponse(status_code=400, content={"error": "text is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        sender = _resolve_current_user_row(request, cur, domain)
        if not sender:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        sender_shop_id = int(sender.get("shop_id") or 0)
        sender_shop_uuid = str(sender.get("shop_uuid") or "").strip() or _resolve_request_shop_uuid(request, cur, domain)
        if not sender_shop_id or not sender_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT id
            FROM shop_users
            WHERE id = %s
              AND active = TRUE
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
            LIMIT 1
            """,
            (recipient_user_id, sender_shop_uuid, sender_shop_id, domain),
        )
        recipient = cur.fetchone() or {}
        if not recipient:
            return JSONResponse(status_code=404, content={"error": "Recipient not found"})

        cur.execute(
            """
            INSERT INTO chat_messages (domain, shop_id, shop_uuid, sender_user_id, recipient_user_id, kind, body)
            VALUES (%s, %s, %s::uuid, %s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (domain, sender_shop_id, sender_shop_uuid, int(sender.get("id") or 0), recipient_user_id, kind, body),
        )
        row = cur.fetchone() or {}
        conn.commit()

        created_at = row.get("created_at")
        created_ts = int(created_at.timestamp() * 1000) if isinstance(created_at, datetime) else int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        return {
            "status": "ok",
            "message": {
                "id": int(row.get("id") or 0),
                "from_user_id": int(sender.get("id") or 0),
                "to_user_id": int(recipient_user_id),
                "kind": kind,
                "text": body,
                "ts": created_ts,
            },
        }
    finally:
        cur.close()



@router.get("/chat/messages")
async def chat_messages(request: Request):
    domain = str(get_user_domain(request) or "").strip().lower()
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        current_user = _resolve_current_user_row(request, cur, domain)
        if not current_user:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        current_user_id = int(current_user.get("id") or 0)
        current_shop_id = int(current_user.get("shop_id") or 0)
        current_shop_uuid = str(current_user.get("shop_uuid") or "").strip() or _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT
                m.id,
                m.sender_user_id,
                m.recipient_user_id,
                m.kind,
                m.body,
                m.read_at,
                m.completed_at,
                m.created_at,
                su.first_name AS sender_first,
                su.last_name AS sender_last,
                ru.first_name AS recipient_first,
                ru.last_name AS recipient_last
            FROM chat_messages m
            LEFT JOIN shop_users su
                ON su.id = m.sender_user_id
            LEFT JOIN shop_users ru
                ON ru.id = m.recipient_user_id
                WHERE (
                          m.shop_uuid = %s::uuid
                      OR (m.shop_uuid IS NULL AND m.shop_id = %s AND m.domain = %s)
                        )
              AND (m.sender_user_id = %s OR m.recipient_user_id = %s)
            ORDER BY m.created_at ASC, m.id ASC
            LIMIT 3000
            """,
                (current_shop_uuid, current_shop_id, domain, current_user_id, current_user_id),
        )
        rows = cur.fetchall() or []

        messages = []
        for row in rows:
            created_at = row.get("created_at")
            ts = int(created_at.timestamp() * 1000) if isinstance(created_at, datetime) else 0
            read_at = row.get("read_at")
            completed_at = row.get("completed_at")
            messages.append(
                {
                    "id": int(row.get("id") or 0),
                    "from_user_id": int(row.get("sender_user_id") or 0),
                    "to_user_id": int(row.get("recipient_user_id") or 0),
                    "kind": str(row.get("kind") or "message"),
                    "text": str(row.get("body") or ""),
                    "ts": ts,
                    "read_at": read_at.isoformat() if isinstance(read_at, datetime) else None,
                    "completed_at": completed_at.isoformat() if isinstance(completed_at, datetime) else None,
                    "from_name": " ".join(part for part in [str(row.get("sender_first") or "").strip(), str(row.get("sender_last") or "").strip()] if part),
                    "to_name": " ".join(part for part in [str(row.get("recipient_first") or "").strip(), str(row.get("recipient_last") or "").strip()] if part),
                }
            )

        return {"messages": messages}
    finally:
        cur.close()



@router.get("/chat/users")
async def chat_users(request: Request):
    domain = str(get_user_domain(request) or "").strip().lower()
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "users": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        current_user = _resolve_current_user_row(request, cur, domain)
        if not current_user:
            return JSONResponse(status_code=401, content={"error": "Not authenticated", "users": []})

        current_shop_id = int(current_user.get("shop_id") or 0)
        current_shop_uuid = str(current_user.get("shop_uuid") or "").strip() or _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "users": []})

        cur.execute(
            """
                        SELECT id, user_id, first_name, last_name, email, role, shop_id, shop_uuid
            FROM shop_users
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND domain = %s AND shop_id = %s)
                                    )
              AND active = TRUE
            ORDER BY first_name ASC, last_name ASC, id ASC
            """,
                        (current_shop_uuid, domain, current_shop_id),
        )
        rows = cur.fetchall() or []
        users = []
        for row in rows:
            row_email = str(row.get("email") or "").strip().lower()
            users.append(
                {
                    "id": int(row.get("id") or 0),
                    "first_name": str(row.get("first_name") or "").strip(),
                    "last_name": str(row.get("last_name") or "").strip(),
                    "email": str(row.get("email") or "").strip(),
                    "role": "ARCHITECT" if _is_architect_email(row_email) else str(row.get("role") or "").strip(),
                    "shop_id": int(row.get("shop_id") or 0) or None,
                    "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                    "user_uuid": str(row.get("user_id") or "").strip() or None,
                }
            )

        return {"users": users}
    finally:
        cur.close()



@router.post("/chat/read")
async def chat_mark_read(request: Request):
    domain = str(get_user_domain(request) or "").strip().lower()
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    try:
        with_user_id = int(data.get("with_user_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "with_user_id is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        current_user = _resolve_current_user_row(request, cur, domain)
        if not current_user:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        current_user_id = int(current_user.get("id") or 0)
        current_shop_id = int(current_user.get("shop_id") or 0)
        current_shop_uuid = str(current_user.get("shop_uuid") or "").strip() or _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            UPDATE chat_messages
            SET read_at = CURRENT_TIMESTAMP
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND recipient_user_id = %s
              AND sender_user_id = %s
              AND read_at IS NULL
            """,
                        (current_shop_uuid, current_shop_id, domain, current_user_id, with_user_id),
        )
        updated = int(cur.rowcount or 0)
        conn.commit()
        return {"status": "ok", "updated": updated}
    finally:
        cur.close()



@router.post("/chat/task/complete")
async def chat_complete_task(request: Request):
    domain = str(get_user_domain(request) or "").strip().lower()
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    try:
        task_id = int(data.get("task_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "task_id is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        current_user = _resolve_current_user_row(request, cur, domain)
        if not current_user:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        current_user_id = int(current_user.get("id") or 0)
        current_shop_id = int(current_user.get("shop_id") or 0)
        current_shop_uuid = str(current_user.get("shop_uuid") or "").strip() or _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            UPDATE chat_messages
            SET completed_at = CURRENT_TIMESTAMP,
                read_at = COALESCE(read_at, CURRENT_TIMESTAMP)
            WHERE id = %s
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND recipient_user_id = %s
              AND kind = 'task'
            """,
                        (task_id, current_shop_uuid, current_shop_id, domain, current_user_id),
        )
        updated = int(cur.rowcount or 0)
        conn.commit()
        if not updated:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        return {"status": "ok"}
    finally:
        cur.close()





