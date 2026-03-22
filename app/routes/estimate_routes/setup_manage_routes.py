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
    build_session_snapshot_payload,
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

@router.get("/setup/shop")
async def get_setup_shop(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        requested_scope_domain = _resolve_setup_scope_domain(request, domain, request.query_params.get("shop_domain"))
        selected_domain = _resolve_effective_shop_domain(
            cur,
            requested_scope_domain,
            allow_fallback=_request_is_architect(request),
        )
        if not selected_domain:
            return {"shop": {}}

        selected_shop_uuid = _resolve_request_shop_uuid(request, cur, selected_domain)
        if selected_shop_uuid:
            cur.execute(
                """
                SELECT shop_id, shop_uuid, shop_name, address, city, state, zip_code, phone, email
                FROM shop_settings
                WHERE (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND domain = %s)
                      )
                LIMIT 1
                """,
                (selected_shop_uuid, selected_domain),
            )
        else:
            cur.execute(
                """
                SELECT shop_id, shop_uuid, shop_name, address, city, state, zip_code, phone, email
                FROM shop_settings
                WHERE domain = %s
                LIMIT 1
                """,
                (selected_domain,),
            )
        row = cur.fetchone() or {}
        return {
            "shop": {
                "shop_id": int(row.get("shop_id") or 0) or None,
                "shop_uuid": str(row.get("shop_uuid") or "").strip() or selected_shop_uuid,
                "shop_name": str(row.get("shop_name") or "").strip(),
                "address": str(row.get("address") or "").strip(),
                "city": str(row.get("city") or "").strip(),
                "state": str(row.get("state") or "").strip(),
                "zip_code": str(row.get("zip_code") or "").strip(),
                "phone": str(row.get("phone") or "").strip(),
                "email": str(row.get("email") or "").strip(),
            }
        }
    finally:
        cur.close()



@router.post("/setup/shop")
async def save_setup_shop(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selected_domain = _resolve_setup_scope_domain(request, domain, data.get("shop_domain"))
    shop_name = str(data.get("shop_name") or "").strip()
    address = str(data.get("address") or "").strip()
    city = str(data.get("city") or "").strip()
    state = str(data.get("state") or "").strip()
    zip_code = str(data.get("zip_code") or "").strip()
    phone = str(data.get("phone") or "").strip()
    email = str(data.get("email") or "").strip()

    if not shop_name or not address or not city or not state or not zip_code:
        return JSONResponse(status_code=400, content={"error": "shop_name, address, city, state, and zip_code are required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        requester_role = str((requester_row or {}).get("role") or "").strip()
        if not requester_is_architect and not _is_manager_or_hr_role(requester_role):
            return JSONResponse(status_code=403, content={"error": "Forbidden"})
        if not requester_is_architect and selected_domain != str(domain or "").strip().lower():
            return JSONResponse(status_code=403, content={"error": "Forbidden"})

        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or shop_row.get("shop_id") or "").strip() or None

        if not selected_shop_id and requester_is_architect:
            cur.execute(
                """
                INSERT INTO shops (shop_id, domain, name, address, city, state, zip, updated_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (domain)
                DO UPDATE SET
                    name = COALESCE(EXCLUDED.name, shops.name),
                    address = COALESCE(EXCLUDED.address, shops.address),
                    city = COALESCE(EXCLUDED.city, shops.city),
                    state = COALESCE(EXCLUDED.state, shops.state),
                    zip = COALESCE(EXCLUDED.zip, shops.zip),
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, shop_id, shop_id AS shop_uuid
                """,
                (str(uuid.uuid4()), selected_domain, shop_name or None, address or None, city or None, state or None, zip_code or None),
            )
            inserted_shop_row = cur.fetchone() or {}
            selected_shop_id = int(inserted_shop_row.get("id") or 0)
            selected_shop_uuid = str(inserted_shop_row.get("shop_uuid") or inserted_shop_row.get("shop_id") or "").strip() or None

        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})
        cur.execute(
            """
            INSERT INTO shop_settings (domain, shop_id, shop_uuid, shop_name, address, city, state, zip_code, phone, email, updated_at)
            VALUES (%s, %s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (domain)
            DO UPDATE SET
                shop_id = EXCLUDED.shop_id,
                shop_uuid = EXCLUDED.shop_uuid,
                shop_name = EXCLUDED.shop_name,
                address = EXCLUDED.address,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                zip_code = EXCLUDED.zip_code,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                selected_domain,
                selected_shop_id,
                selected_shop_uuid,
                shop_name or None,
                address or None,
                city or None,
                state or None,
                zip_code or None,
                phone or None,
                email or None,
            ),
        )
        cur.execute(
            """
            UPDATE shops
            SET name = %s,
                address = %s,
                city = %s,
                state = %s,
                zip = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (shop_name or None, address or None, city or None, state or None, zip_code or None, selected_shop_id),
        )
        conn.commit()
        authenticated_user = get_authenticated_user(request) or {}
        role_value = str((requester_row or {}).get("role") or authenticated_user.get("role") or "").strip()
        user_uuid_value = str(authenticated_user.get("user_uuid") or "").strip() or None
        permissions = build_permission_snapshot(
            role=role_value,
            domain=selected_domain,
            shop_id=selected_shop_id,
            shop_uuid=selected_shop_uuid,
            user_uuid=user_uuid_value,
            is_architect=requester_is_architect,
        )
        snapshot_user = {
            "id": int(authenticated_user.get("id") or (requester_row or {}).get("id") or 0),
            "email": str(authenticated_user.get("email") or (requester_row or {}).get("email") or "").strip().lower(),
            "first_name": str(authenticated_user.get("first_name") or (requester_row or {}).get("first_name") or "").strip(),
            "last_name": str(authenticated_user.get("last_name") or (requester_row or {}).get("last_name") or "").strip(),
            "role": role_value,
            "domain": selected_domain,
            "shop_id": selected_shop_id,
            "shop_uuid": selected_shop_uuid,
            "user_uuid": user_uuid_value,
            "shop_name": shop_name,
            "address": address,
            "access_level": str(permissions.get("access_level") or "").strip(),
            "permissions": permissions,
            "is_architect": requester_is_architect,
        }
        session_snapshot = build_session_snapshot_payload(
            user=snapshot_user,
            permission_snapshot=permissions,
        )
        request.state.session_snapshot = session_snapshot
        request.state.permission_snapshot = permissions
        return {"status": "ok", "shop_uuid": selected_shop_uuid, "session_snapshot": session_snapshot}
    finally:
        cur.close()



@router.get("/setup/context")
async def get_setup_context(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    authenticated_user = get_authenticated_user(request) or {}
    shop_id = int(authenticated_user.get("shop_id") or 0) or None
    shop_uuid = str(authenticated_user.get("shop_uuid") or "").strip() or None
    default_domain = str(domain or "").strip().lower()

    if _request_is_architect(request):
        conn = get_conn()
        cur = conn.cursor()
        try:
            effective_domain = _resolve_effective_shop_domain(cur, default_domain, allow_fallback=True)
            if effective_domain:
                default_domain = effective_domain
                _dflt_scope = resolve_request_scope(request, cur, domain=default_domain)
                resolved_shop_id = _dflt_scope["shop_id"]
                resolved_shop_uuid = _dflt_scope["shop_uuid"]
                if resolved_shop_id:
                    shop_id = resolved_shop_id
                if resolved_shop_uuid:
                    shop_uuid = resolved_shop_uuid
        finally:
            cur.close()

    return {
        "is_architect": _request_is_architect(request),
        "default_domain": default_domain,
        "default_shop_id": shop_id,
        "default_shop_uuid": shop_uuid,
    }



@router.get("/setup/shops")
async def list_setup_shops(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "shops": []})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden", "shops": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            WITH all_domains AS (
                SELECT DISTINCT domain FROM shop_settings
                UNION
                SELECT DISTINCT domain FROM shop_users
            )
            SELECT
                sh.id AS shop_id,
                d.domain,
                COALESCE(sh.active, TRUE) AS active,
                COALESCE(s.shop_name, sh.name) AS shop_name,
                COALESCE(s.address, sh.address) AS address,
                COALESCE(s.city, sh.city) AS city,
                COALESCE(s.state, sh.state) AS state,
                COALESCE(s.zip_code, sh.zip) AS zip_code,
                s.phone,
                s.email
            FROM all_domains d
            LEFT JOIN shops sh ON sh.domain = d.domain
            LEFT JOIN shop_settings s ON s.domain = d.domain
            ORDER BY LOWER(COALESCE(NULLIF(s.shop_name, ''), NULLIF(sh.name, ''), d.domain)) ASC
            """
        )
        rows = cur.fetchall() or []
        shops = []
        for row in rows:
            shops.append(
                {
                    "id": int(row.get("shop_id") or 0) or None,
                    "domain": str(row.get("domain") or "").strip().lower(),
                    "active": bool(row.get("active", True)),
                    "shop_name": str(row.get("shop_name") or "").strip(),
                    "address": str(row.get("address") or "").strip(),
                    "city": str(row.get("city") or "").strip(),
                    "state": str(row.get("state") or "").strip(),
                    "zip_code": str(row.get("zip_code") or "").strip(),
                    "phone": str(row.get("phone") or "").strip(),
                    "email": str(row.get("email") or "").strip(),
                }
            )
        return {"shops": shops}
    finally:
        cur.close()



@router.get("/manage/shops")
async def list_manage_shops(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "shops": []})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden", "shops": []})

    max_attempts = 3
    for attempt in range(max_attempts):
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                WITH all_domains AS (
                    SELECT DISTINCT domain FROM shops
                    UNION
                    SELECT DISTINCT domain FROM shop_settings
                    UNION
                    SELECT DISTINCT domain FROM shop_users
                )
                SELECT
                    sh.id AS shop_id,
                    d.domain,
                    COALESCE(sh.active, TRUE) AS active,
                    COALESCE(ss.shop_name, sh.name, d.domain) AS shop_name,
                    COUNT(DISTINCT su.id) FILTER (WHERE su.active = TRUE) AS user_count
                FROM all_domains d
                LEFT JOIN shops sh ON sh.domain = d.domain
                LEFT JOIN shop_settings ss ON ss.domain = d.domain
                LEFT JOIN shop_users su ON su.domain = d.domain
                GROUP BY sh.id, d.domain, sh.active, ss.shop_name, sh.name
                ORDER BY LOWER(COALESCE(NULLIF(ss.shop_name, ''), NULLIF(sh.name, ''), d.domain)) ASC
                """
            )
            rows = cur.fetchall() or []
            shops = []
            for row in rows:
                shops.append(
                    {
                        "id": int(row.get("shop_id") or 0) or None,
                        "domain": str(row.get("domain") or "").strip().lower(),
                        "shop_name": str(row.get("shop_name") or "").strip(),
                        "active": bool(row.get("active", True)),
                        "user_count": int(row.get("user_count") or 0),
                    }
                )
            return {"shops": shops}
        except Exception:
            if attempt >= max_attempts - 1:
                return JSONResponse(status_code=500, content={"error": "Unable to load shops", "shops": []})
            await asyncio.sleep(0.25)
        finally:
            cur.close()



@router.get("/manage/users")
async def list_manage_users(request: Request, shop_domain: str | None = None):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "users": []})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden", "users": []})

    max_attempts = 3
    for attempt in range(max_attempts):
        conn = get_conn()
        cur = conn.cursor()
        try:
            selected_domain = _resolve_effective_shop_domain(
                cur,
                str(shop_domain or "").strip().lower(),
                allow_fallback=True,
            )
            if not selected_domain:
                return {"users": []}
            cur.execute(
                """
                SELECT
                    su.id,
                    su.first_name,
                    su.last_name,
                    su.email,
                    su.role,
                    su.shop_id,
                    COALESCE(ss.shop_name, sh.name, su.domain) AS shop_name
                FROM shop_users su
                LEFT JOIN shops sh ON sh.id = su.shop_id
                LEFT JOIN shop_settings ss ON ss.shop_id = su.shop_id AND ss.domain = su.domain
                WHERE su.domain = %s
                  AND su.active = TRUE
                ORDER BY su.created_at DESC, su.id DESC
                """,
                (selected_domain,),
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
                        "shop_name": str(row.get("shop_name") or "").strip(),
                        "shop_id": int(row.get("shop_id") or 0) or None,
                    }
                )
            return {"users": users}
        except Exception:
            if attempt >= max_attempts - 1:
                return JSONResponse(status_code=500, content={"error": "Unable to load users", "users": []})
            await asyncio.sleep(0.25)
        finally:
            cur.close()



@router.post("/manage/shops/active")
async def update_manage_shop_active(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    selected_domain = str(data.get("shop_domain") or "").strip().lower()
    active = bool(data.get("active", True))
    if not selected_domain:
        return JSONResponse(status_code=400, content={"error": "shop_domain is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO shops (domain, active, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (domain)
            DO UPDATE SET
                active = EXCLUDED.active,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, domain, active
            """,
            (selected_domain, active),
        )
        row = cur.fetchone() or {}
        conn.commit()
        return {
            "status": "ok",
            "shop": {
                "id": int(row.get("id") or 0) or None,
                "domain": str(row.get("domain") or "").strip().lower(),
                "active": bool(row.get("active", True)),
            },
        }
    finally:
        cur.close()



@router.post("/manage/users/update")
async def update_manage_user(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    try:
        user_id = int(data.get("id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "id is required"})

    selected_domain = str(data.get("shop_domain") or "").strip().lower()
    first_name = str(data.get("first_name") or "").strip()
    last_name = str(data.get("last_name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    role = str(data.get("role") or "").strip()

    allowed_roles = {"Manager", "Estimator", "Tech", "Receptionist", "HR", "Support"}
    if not selected_domain or not first_name or not last_name or not email or role not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "shop_domain, first_name, last_name, email, and valid role are required"})
    if _is_architect_email(email):
        return JSONResponse(status_code=400, content={"error": "This email cannot be assigned from Manage"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})

        cur.execute(
            """
            UPDATE shop_users
            SET first_name = %s,
                last_name = %s,
                email = %s,
                role = %s,
                domain = %s,
                                shop_id = %s,
                                shop_uuid = %s::uuid
            WHERE id = %s
              AND active = TRUE
                        RETURNING id, user_id, first_name, last_name, email, role, domain, shop_id, shop_uuid
            """,
                        (first_name, last_name, email, role, selected_domain, selected_shop_id, selected_shop_uuid, user_id),
        )
        row = cur.fetchone() or {}
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "User not found"})

        return {
            "status": "ok",
            "user": {
                "id": int(row.get("id") or 0),
                "first_name": str(row.get("first_name") or "").strip(),
                "last_name": str(row.get("last_name") or "").strip(),
                "email": str(row.get("email") or "").strip(),
                "role": str(row.get("role") or "").strip(),
                "shop_id": int(row.get("shop_id") or 0) or None,
                "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                "user_uuid": str(row.get("user_id") or "").strip() or None,
                "shop_domain": str(row.get("domain") or "").strip().lower(),
            },
        }
    finally:
        cur.close()



@router.post("/manage/users")
async def create_manage_user(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    selected_domain = str(data.get("shop_domain") or "").strip().lower()
    first_name = str(data.get("first_name") or "").strip()
    last_name = str(data.get("last_name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    role = str(data.get("role") or "").strip()
    password = str(data.get("password") or "").strip()
    allowed_roles = {"Manager", "Estimator", "Tech", "Receptionist", "HR", "Support"}

    if not selected_domain or not first_name or not last_name or not email or not role or not password:
        return JSONResponse(status_code=400, content={"error": "shop_domain, first_name, last_name, email, role, and password are required"})
    if role not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "Invalid role"})
    if _is_architect_email(email):
        return JSONResponse(status_code=400, content={"error": "This email cannot be assigned from Manage"})

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})

        cur.execute(
            """
            INSERT INTO shop_users (user_id, first_name, last_name, email, role, password_hash, domain, shop_id, shop_uuid, active)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::uuid, TRUE)
            RETURNING id, user_id, first_name, last_name, email, role, shop_id, shop_uuid
            """,
            (str(uuid.uuid4()), first_name, last_name, email, role, password_hash, selected_domain, selected_shop_id, selected_shop_uuid),
        )
        row = cur.fetchone() or {}
        conn.commit()
        return {
            "status": "ok",
            "user": {
                "id": int(row.get("id") or 0),
                "first_name": str(row.get("first_name") or "").strip(),
                "last_name": str(row.get("last_name") or "").strip(),
                "email": str(row.get("email") or "").strip(),
                "role": str(row.get("role") or "").strip(),
                "shop_id": int(row.get("shop_id") or 0) or None,
                "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                "user_uuid": str(row.get("user_id") or "").strip() or None,
            },
        }
    except Exception as exc:
        conn.rollback()
        message = str(exc)
        if "idx_shop_users_shop_id_email_unique" in message or "idx_shop_users_domain_email_unique" in message:
            return JSONResponse(status_code=400, content={"error": "User with that email already exists for this shop"})
        return JSONResponse(status_code=500, content={"error": "Unable to create user"})
    finally:
        cur.close()



@router.post("/manage/users/reset-password")
async def reset_manage_user_password(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    selected_domain = str(data.get("shop_domain") or "").strip().lower()
    user_ids_raw = data.get("user_ids") or []
    new_password = str(data.get("new_password") or "")

    if not selected_domain:
        return JSONResponse(status_code=400, content={"error": "shop_domain is required"})
    if not isinstance(user_ids_raw, list) or not user_ids_raw:
        return JSONResponse(status_code=400, content={"error": "user_ids is required"})
    if not new_password:
        return JSONResponse(status_code=400, content={"error": "new_password is required"})

    user_ids = []
    for value in user_ids_raw:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed not in user_ids:
            user_ids.append(parsed)

    if not user_ids:
        return JSONResponse(status_code=400, content={"error": "No valid user ids provided"})

    password_hash = hashlib.sha256(new_password.encode("utf-8")).hexdigest()

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})

        cur.execute(
            """
            UPDATE shop_users
            SET password_hash = %s
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND active = TRUE
              AND id = ANY(%s)
            """,
            (password_hash, selected_shop_uuid, selected_shop_id, selected_domain, user_ids),
        )
        updated_count = int(cur.rowcount or 0)
        conn.commit()
        return {"status": "ok", "updated": updated_count}
    finally:
        cur.close()



@router.post("/manage/delete")
async def delete_manage_entities(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    user_ids = []
    for value in data.get("user_ids") or []:
        try:
            user_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    shop_domains = [str(value or "").strip().lower() for value in (data.get("shop_domains") or []) if str(value or "").strip()]

    if not user_ids and not shop_domains:
        return JSONResponse(status_code=400, content={"error": "No users or shops selected"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        deleted_users = 0
        deleted_shops = 0

        if user_ids:
            cur.execute(
                """
                UPDATE shop_users
                SET active = FALSE
                WHERE id = ANY(%s)
                  AND active = TRUE
                """,
                (user_ids,),
            )
            deleted_users += int(cur.rowcount or 0)

        if shop_domains:
            cur.execute(
                """
                UPDATE shop_users
                SET active = FALSE
                WHERE domain = ANY(%s)
                  AND active = TRUE
                """,
                (shop_domains,),
            )
            deleted_users += int(cur.rowcount or 0)

            cur.execute("DELETE FROM shop_settings WHERE domain = ANY(%s)", (shop_domains,))
            cur.execute("DELETE FROM shops WHERE domain = ANY(%s)", (shop_domains,))
            deleted_shops = int(cur.rowcount or 0)

        conn.commit()
        return {"status": "ok", "deleted_users": deleted_users, "deleted_shops": deleted_shops}
    finally:
        cur.close()



@router.post("/setup/users/update")
async def update_setup_user(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selected_domain = _resolve_setup_scope_domain(request, domain, data.get("shop_domain"))
    user_id = data.get("id")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "id is required"})

    first_name = str(data.get("first_name") or "").strip()
    last_name = str(data.get("last_name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    role = str(data.get("role") or "").strip()

    allowed_roles = {"Manager", "Estimator", "Tech", "Receptionist", "HR", "Support"}
    if not first_name or not last_name or not email or not role:
        return JSONResponse(status_code=400, content={"error": "first_name, last_name, email, and role are required"})
    if role not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "Invalid role"})
    if _is_architect_email(email):
        return JSONResponse(status_code=400, content={"error": "This email cannot be assigned from Setup"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        requester_role = str((requester_row or {}).get("role") or "").strip()
        if not (requester_is_architect or _is_manager_or_hr_role(requester_role)):
            return JSONResponse(status_code=403, content={"error": "Forbidden"})

        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})
        cur.execute(
            """
            UPDATE shop_users
            SET first_name = %s,
                last_name = %s,
                email = %s,
                                role = %s,
                                shop_uuid = %s::uuid
            WHERE id = %s
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND active = TRUE
                        RETURNING id, user_id, first_name, last_name, email, role, shop_id, shop_uuid, created_at
            """,
                                                (first_name, last_name, email, role, selected_shop_uuid, user_id, selected_shop_uuid, selected_shop_id, selected_domain),
        )
        row = cur.fetchone() or {}
        conn.commit()

        if not row:
            return JSONResponse(status_code=404, content={"error": "User not found"})

        created_at = row.get("created_at")
        return {
            "status": "ok",
            "user": {
                "id": int(row.get("id") or 0),
                "first_name": str(row.get("first_name") or "").strip(),
                "last_name": str(row.get("last_name") or "").strip(),
                "email": str(row.get("email") or "").strip(),
                "role": str(row.get("role") or "").strip(),
                "shop_id": int(row.get("shop_id") or 0) or None,
                "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                "user_uuid": str(row.get("user_id") or "").strip() or None,
                "created_at": created_at.isoformat() if isinstance(created_at, datetime) else None,
            },
        }
    finally:
        cur.close()



@router.post("/setup/users/reset-password")
async def reset_setup_user_password(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selected_domain = _resolve_setup_scope_domain(request, domain, data.get("shop_domain"))
    user_ids_raw = data.get("user_ids") or []
    new_password = str(data.get("new_password") or "")

    if not isinstance(user_ids_raw, list) or not user_ids_raw:
        return JSONResponse(status_code=400, content={"error": "user_ids is required"})
    if not new_password:
        return JSONResponse(status_code=400, content={"error": "new_password is required"})

    user_ids = []
    for value in user_ids_raw:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed not in user_ids:
            user_ids.append(parsed)

    if not user_ids:
        return JSONResponse(status_code=400, content={"error": "No valid user ids provided"})

    password_hash = hashlib.sha256(new_password.encode("utf-8")).hexdigest()

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        requester_role = str(requester_row.get("role") or "").strip()
        if not (requester_is_architect or _is_manager_or_hr_role(requester_role)):
            return JSONResponse(status_code=403, content={"error": "Forbidden"})

        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})
        cur.execute(
            """
            UPDATE shop_users
            SET password_hash = %s
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND active = TRUE
              AND id = ANY(%s)
            """,
                                                (password_hash, selected_shop_uuid, selected_shop_id, selected_domain, user_ids),
        )
        updated_count = int(cur.rowcount or 0)
        conn.commit()
        return {"status": "ok", "updated": updated_count}
    finally:
        cur.close()



@router.get("/setup/users")
async def list_setup_users(request: Request, shop_domain: str | None = None):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "users": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated", "users": []})
        requester_role = str((requester_row or {}).get("role") or "").strip()
        if not (requester_is_architect or _is_manager_or_hr_role(requester_role)):
            return JSONResponse(status_code=403, content={"error": "Forbidden", "users": []})

        requested_scope_domain = _resolve_setup_scope_domain(request, domain, shop_domain)
        selected_domain = _resolve_effective_shop_domain(
            cur,
            requested_scope_domain,
            allow_fallback=requester_is_architect,
        )
        if not selected_domain:
            return {"users": []}

        _users_scope = resolve_request_scope(request, cur, domain=selected_domain)
        current_shop_uuid = _users_scope["shop_uuid"]
        if not current_shop_uuid:
            return {"users": []}
        cur.execute(
            """
                        SELECT id, user_id, first_name, last_name, email, role, shop_id, shop_uuid, created_at
            FROM shop_users
                        WHERE shop_uuid = %s::uuid
              AND active = TRUE
            ORDER BY created_at DESC, id DESC
            """,
                        (current_shop_uuid,),
        )
        rows = cur.fetchall() or []
        users = []
        for row in rows:
            created_at = row.get("created_at")
            row_email = str(row.get("email") or "").strip().lower()
            row_is_architect_user = _is_architect_email(row_email)
            display_role = "ARCHITECT" if row_is_architect_user else str(row.get("role") or "").strip()
            role_locked = bool(row_is_architect_user)
            users.append(
                {
                    "id": int(row.get("id") or 0),
                    "first_name": str(row.get("first_name") or "").strip(),
                    "last_name": str(row.get("last_name") or "").strip(),
                    "email": str(row.get("email") or "").strip(),
                    "role": display_role,
                    "shop_id": int(row.get("shop_id") or 0) or None,
                    "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                    "user_uuid": str(row.get("user_id") or "").strip() or None,
                    "role_locked": role_locked,
                    "created_at": created_at.isoformat() if isinstance(created_at, datetime) else None,
                }
            )
        return {"users": users}
    finally:
        cur.close()



@router.post("/setup/users")
async def create_setup_user(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selected_domain = _resolve_setup_scope_domain(request, domain, data.get("shop_domain"))
    first_name = str(data.get("first_name") or "").strip()
    last_name = str(data.get("last_name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    role = str(data.get("role") or "").strip()
    password = str(data.get("password") or "")

    allowed_roles = {"Manager", "Estimator", "Tech", "Receptionist", "HR", "Support"}
    if not first_name or not last_name or not email or not role or not password:
        return JSONResponse(status_code=400, content={"error": "first_name, last_name, email, role, and password are required"})
    if role not in allowed_roles:
        return JSONResponse(status_code=400, content={"error": "Invalid role"})
    if _is_architect_email(email):
        return JSONResponse(status_code=400, content={"error": "This email cannot be created from Setup"})

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        requester_role = str((requester_row or {}).get("role") or "").strip()
        if not (requester_is_architect or _is_manager_or_hr_role(requester_role)):
            return JSONResponse(status_code=403, content={"error": "Forbidden"})

        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})
        cur.execute(
            """
            INSERT INTO shop_users (user_id, first_name, last_name, email, role, password_hash, domain, shop_id, shop_uuid, active)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::uuid, TRUE)
            ON CONFLICT (domain, email)
            DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                role = EXCLUDED.role,
                shop_id = EXCLUDED.shop_id,
                shop_uuid = EXCLUDED.shop_uuid,
                password_hash = EXCLUDED.password_hash,
                active = TRUE
            RETURNING id, user_id, first_name, last_name, email, role, shop_id, shop_uuid, created_at
            """,
            (str(uuid.uuid4()), first_name, last_name, email, role, password_hash, selected_domain, selected_shop_id, selected_shop_uuid),
        )
        row = cur.fetchone() or {}
        conn.commit()

        created_at = row.get("created_at")
        return {
            "status": "ok",
            "user": {
                "id": int(row.get("id") or 0),
                "first_name": str(row.get("first_name") or "").strip(),
                "last_name": str(row.get("last_name") or "").strip(),
                "email": str(row.get("email") or "").strip(),
                "role": str(row.get("role") or "").strip(),
                "shop_id": int(row.get("shop_id") or 0) or None,
                "shop_uuid": str(row.get("shop_uuid") or "").strip() or None,
                "user_uuid": str(row.get("user_id") or "").strip() or None,
                "created_at": created_at.isoformat() if isinstance(created_at, datetime) else None,
            },
        }
    finally:
        cur.close()



@router.post("/setup/users/delete")
async def delete_setup_users(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    selected_domain = _resolve_setup_scope_domain(request, domain, data.get("shop_domain"))
    user_ids_raw = data.get("user_ids") or []

    if not isinstance(user_ids_raw, list) or not user_ids_raw:
        return JSONResponse(status_code=400, content={"error": "user_ids is required"})

    user_ids = []
    for value in user_ids_raw:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed not in user_ids:
            user_ids.append(parsed)

    if not user_ids:
        return JSONResponse(status_code=400, content={"error": "No valid user ids provided"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        requester_is_architect = _request_is_architect(request)
        requester_row = _resolve_current_user_row(request, cur, domain)
        if not requester_row and not requester_is_architect:
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        requester_role = str((requester_row or {}).get("role") or "").strip()
        if not (requester_is_architect or _is_manager_or_hr_role(requester_role)):
            return JSONResponse(status_code=403, content={"error": "Forbidden"})

        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None
        if not selected_shop_id or not selected_shop_uuid:
            return JSONResponse(status_code=400, content={"error": "Unable to resolve shop scope"})

        cur.execute(
            """
            SELECT id
            FROM shop_users
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND id = ANY(%s)
              AND active = TRUE
              AND LOWER(email) <> %s
            """,
                                                (selected_shop_uuid, selected_shop_id, selected_domain, user_ids, _ARCHITECT_EMAIL),
        )
        deletable_ids = [int((row or {}).get("id") or 0) for row in (cur.fetchall() or [])]
        deletable_ids = [value for value in deletable_ids if value > 0]
        if not deletable_ids:
            return JSONResponse(status_code=404, content={"error": "No deletable users found"})

        cur.execute(
            "DELETE FROM auth_sessions WHERE user_id = ANY(%s)",
            (deletable_ids,),
        )

        cur.execute(
            """
            DELETE FROM shop_users
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND id = ANY(%s)
            """,
                                                (selected_shop_uuid, selected_shop_id, selected_domain, deletable_ids),
        )
        deleted_count = int(cur.rowcount or 0)
        conn.commit()
        return {"status": "ok", "deleted": deleted_count}
    finally:
        cur.close()



@router.post("/setup/shops/delete")
async def delete_setup_shop(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not _request_is_architect(request):
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    selected_domain = str(data.get("shop_domain") or "").strip().lower()
    if not selected_domain:
        return JSONResponse(status_code=400, content={"error": "shop_domain is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, shop_id, shop_id AS shop_uuid FROM shops WHERE domain = %s LIMIT 1", (selected_domain,))
        shop_row = cur.fetchone() or {}
        selected_shop_id = int(shop_row.get("id") or 0)
        selected_shop_uuid = str(shop_row.get("shop_uuid") or "").strip() or None

        if not selected_shop_id:
            return JSONResponse(status_code=404, content={"error": "Shop not found"})

        if selected_shop_uuid:
            cur.execute(
                """
                DELETE FROM shop_settings
                WHERE shop_uuid = %s::uuid
                   OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                """,
                (selected_shop_uuid, selected_shop_id, selected_domain),
            )
        else:
            cur.execute("DELETE FROM shop_settings WHERE domain = %s", (selected_domain,))
        settings_deleted = int(cur.rowcount or 0)

        if selected_shop_uuid:
            cur.execute(
                """
                DELETE FROM shop_users
                WHERE shop_uuid = %s::uuid
                   OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                """,
                (selected_shop_uuid, selected_shop_id, selected_domain),
            )
        else:
            cur.execute("DELETE FROM shop_users WHERE domain = %s", (selected_domain,))
        users_deleted = int(cur.rowcount or 0)

        cur.execute("DELETE FROM shops WHERE id = %s", (selected_shop_id,))
        shops_deleted = int(cur.rowcount or 0)

        conn.commit()
        return {
            "status": "ok",
            "deleted": {
                "shop_settings": settings_deleted,
                "shop_users": users_deleted,
                "shops": shops_deleted,
            },
        }
    finally:
        cur.close()





