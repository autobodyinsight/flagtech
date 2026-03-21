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
    build_session_snapshot_payload,
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

@router.post("/auth/login")
async def auth_login(request: Request):
    data = await request.json()
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")

    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "email and password are required"})

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
                        SELECT
                                su.id,
                                su.user_id,
                                su.first_name,
                                su.last_name,
                                su.email,
                                su.role,
                                su.domain,
                                su.shop_id,
                                su.shop_uuid,
                                COALESCE(sh.active, TRUE) AS shop_active
                        FROM shop_users su
                        LEFT JOIN shops sh
                            ON sh.id = su.shop_id
                        WHERE LOWER(su.email) = %s
                            AND su.password_hash = %s
                            AND su.active = TRUE
                        ORDER BY su.created_at DESC, su.id DESC
            LIMIT 1
            """,
            (email, password_hash),
        )
        row = cur.fetchone() or {}
        if not row:
            return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

        if not bool(row.get("shop_active", True)):
            return JSONResponse(status_code=403, content={"error": "LOG IN NOT AUTHORIZED, CONTACT SUPPORT"})

        user_email = str(row.get("email") or "").strip().lower()
        user_domain = str(row.get("domain") or "").strip().lower()
        first_name = str(row.get("first_name") or "").strip()
        last_name = str(row.get("last_name") or "").strip()
        user_role = str(row.get("role") or "").strip()
        user_shop_id = int(row.get("shop_id") or 0)
        user_shop_uuid = str(row.get("shop_uuid") or "").strip() or None
        user_uuid = str(row.get("user_id") or "").strip() or None
        permission_snapshot = build_permission_snapshot(
            role=user_role,
            domain=user_domain,
            shop_id=user_shop_id,
            shop_uuid=user_shop_uuid,
            user_uuid=user_uuid,
            is_architect=_is_architect_email(user_email),
        )

        if not user_email or not user_domain or not user_shop_id:
            return JSONResponse(status_code=401, content={"error": "Invalid user record"})

        secure = _build_cookie_secure_flag(request)
        session_id = create_auth_session(int(row.get("id") or 0), permission_snapshot=permission_snapshot)
        response = JSONResponse(
            content={
                "status": "ok",
                "session_snapshot": build_session_snapshot_payload(
                    user={
                        "id": int(row.get("id") or 0),
                        "email": user_email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": user_role,
                        "domain": user_domain,
                        "shop_id": user_shop_id,
                        "shop_uuid": user_shop_uuid,
                        "user_uuid": user_uuid,
                        "shop_name": "",
                        "address": "",
                        "access_level": permission_snapshot.get("access_level"),
                        "permissions": permission_snapshot,
                        "is_architect": _is_architect_email(user_email),
                    },
                    permission_snapshot=permission_snapshot,
                ),
                "user": {
                    "id": int(row.get("id") or 0),
                    "email": user_email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": user_role,
                    "domain": user_domain,
                    "shop_id": user_shop_id,
                    "shop_uuid": user_shop_uuid,
                    "user_uuid": user_uuid,
                    "access_level": permission_snapshot.get("access_level"),
                    "permissions": permission_snapshot,
                },
            }
        )
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=60 * 60 * 12,
            path="/",
        )
        response.set_cookie(
            key="user_email",
            value=user_email,
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=60 * 60 * 12,
            path="/",
        )
        response.set_cookie(
            key="user_domain",
            value=user_domain,
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=60 * 60 * 12,
            path="/",
        )
        response.set_cookie(
            key="user_shop_id",
            value=str(user_shop_id),
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=60 * 60 * 12,
            path="/",
        )
        return response
    finally:
        cur.close()



@router.post("/auth/logout")
async def auth_logout(request: Request):
    secure = _build_cookie_secure_flag(request)
    revoke_auth_session(request.cookies.get(SESSION_COOKIE_NAME))
    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie(SESSION_COOKIE_NAME, path="/", secure=secure, samesite="lax")
    response.delete_cookie("user_email", path="/", secure=secure, samesite="lax")
    response.delete_cookie("user_domain", path="/", secure=secure, samesite="lax")
    response.delete_cookie("user_shop_id", path="/", secure=secure, samesite="lax")
    return response



@router.get("/auth/session")
async def auth_session(request: Request):
    authenticated_user = get_authenticated_user(request)
    if not authenticated_user:
        return JSONResponse(status_code=401, content={"authenticated": False})
    email_value = str(authenticated_user.get("email") or "").strip().lower()
    role_value = str(authenticated_user.get("role") or "").strip()
    domain_value = str(authenticated_user.get("domain") or "").strip().lower()
    shop_id_value = int(authenticated_user.get("shop_id") or 0) or None
    shop_uuid_value = str(authenticated_user.get("shop_uuid") or "").strip() or None
    user_uuid_value = str(authenticated_user.get("user_uuid") or "").strip() or None

    permissions = build_permission_snapshot(
        role=role_value,
        domain=domain_value,
        shop_id=shop_id_value,
        shop_uuid=shop_uuid_value,
        user_uuid=user_uuid_value,
        is_architect=_is_architect_email(email_value),
    )

    snapshot_user = {
        "id": int(authenticated_user.get("id") or 0),
        "email": email_value,
        "first_name": str(authenticated_user.get("first_name") or "").strip(),
        "last_name": str(authenticated_user.get("last_name") or "").strip(),
        "role": role_value,
        "domain": domain_value,
        "shop_id": shop_id_value,
        "shop_uuid": shop_uuid_value,
        "user_uuid": user_uuid_value,
        "shop_name": str(authenticated_user.get("shop_name") or "").strip(),
        "address": str(authenticated_user.get("address") or "").strip(),
        "access_level": str(permissions.get("access_level") or "").strip(),
        "permissions": permissions,
        "is_architect": _is_architect_email(email_value),
    }

    session_snapshot = build_session_snapshot_payload(
        user=snapshot_user,
        permission_snapshot=permissions,
    )

    request.state.session_snapshot = session_snapshot
    request.state.permission_snapshot = permissions

    return {
        "authenticated": True,
        "session_snapshot": session_snapshot,
        "user": snapshot_user,
    }


