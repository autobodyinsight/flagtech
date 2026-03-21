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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            """
            INSERT INTO parts_vendors (name, vendor_type, contact_person, phone, street, city, state, zip, domain, shop_id, shop_uuid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
            RETURNING id, name, vendor_type, contact_person, phone, street, city, state, zip, active
            """,
            (
                name,
                vendor_type or None,
                contact_person or None,
                phone or None,
                street or None,
                city or None,
                state or None,
                zip_code or None,
                domain,
                current_shop_id,
                current_shop_uuid,
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "vendors": []})
        cur.execute(
            """
            SELECT id, name, vendor_type, contact_person, phone, street, city, state, zip, active
            FROM parts_vendors
                        WHERE active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            ORDER BY name
            """,
                        (current_shop_uuid, current_shop_id, domain),
        )

        rows = cur.fetchall()
        vendors = [
            {
                "id": row["id"],
                "name": row["name"],
                "vendor_type": row["vendor_type"],
                "contact_person": row["contact_person"],
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
    street = (data.get("street") or "").strip()
    city = (data.get("city") or "").strip()
    state = (data.get("state") or "").strip()
    zip_code = (data.get("zip") or "").strip()

    if not name:
        return JSONResponse(status_code=400, content={"error": "Vendor name is required"})

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
            UPDATE parts_vendors
            SET
                name = %s,
                vendor_type = %s,
                contact_person = %s,
                phone = %s,
                street = %s,
                city = %s,
                state = %s,
                zip = %s
                        WHERE id = %s
                            AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            RETURNING id, name, vendor_type, contact_person, phone, street, city, state, zip, active
            """,
            (
                name,
                vendor_type or None,
                contact_person or None,
                phone or None,
                street or None,
                city or None,
                state or None,
                zip_code or None,
                vendor_id,
                current_shop_uuid,
                current_shop_id,
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
                "street": row["street"],
                "city": row["city"],
                "state": row["state"],
                "zip": row["zip"],
                "active": row["active"],
            }
        }
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "invoices": []})

        cur.execute(
            """
            SELECT name
            FROM parts_vendors
                        WHERE id = %s
                            AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            LIMIT 1
            """,
                        (vendor_id, current_shop_uuid, current_shop_id, domain),
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
                COALESCE(NULLIF(BTRIM(invoice_number), ''), ro) AS invoice_number,
                MAX(COALESCE(received_business_date, received_at::date)) AS invoice_date,
                COALESCE(SUM(cost), 0) AS total_cost
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND LOWER(TRIM(vendor)) = LOWER(TRIM(%s))
            GROUP BY COALESCE(NULLIF(BTRIM(invoice_number), ''), ro)
            ORDER BY MAX(COALESCE(received_business_date, received_at::date)) DESC
            """,
                        (current_shop_uuid, current_shop_id, domain, vendor_name),
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
        _scope = resolve_request_scope(request, cur, domain=domain)
        current_shop_id = _scope["shop_id"]
        current_shop_uuid = _scope["shop_uuid"]
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "parts": []})

        cur.execute(
            """
            SELECT name
            FROM parts_vendors
                        WHERE id = %s
                            AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            LIMIT 1
            """,
                        (vendor_id, current_shop_uuid, current_shop_id, domain),
        )
        vendor_row = cur.fetchone()
        if not vendor_row:
            return JSONResponse(status_code=404, content={"error": "Vendor not found", "parts": []})

        vendor_name = (vendor_row.get("name") or "").strip()
        if not vendor_name:
            return {"parts": []}

        cur.execute(
            """
            SELECT ro, line_id, cost, received_at
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND LOWER(TRIM(vendor)) = LOWER(TRIM(%s))
              AND (
                COALESCE(NULLIF(BTRIM(invoice_number), ''), ro) = %s
                OR ro = %s
              )
            ORDER BY line_id
            """,
                        (current_shop_uuid, current_shop_id, domain, vendor_name, invoice_value, invoice_value),
        )
        rows = cur.fetchall() or []

        ro_candidates = [str(row.get("ro") or "").strip() for row in rows if str(row.get("ro") or "").strip()]
        ro_for_lookup = ro_candidates[0] if ro_candidates else ""

        parts_repairs = []
        if ro_for_lookup:
            cur.execute(
                """
                SELECT parts_repairs
                FROM saved_estimates
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                                    AND ro = %s
                ORDER BY saved_at DESC, id DESC
                LIMIT 1
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_for_lookup),
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





