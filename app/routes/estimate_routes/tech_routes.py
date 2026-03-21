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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute("""
            INSERT INTO techs (first_name, last_name, pay_rate, domain, shop_id, shop_uuid, status, role, total_ros)
            VALUES (%s, %s, %s, %s, %s, %s::uuid, 'Active', %s, 0)
            RETURNING id, first_name, last_name, pay_rate, active, status, role, total_ros
        """, (
            data["first_name"],
            data["last_name"],
            data["pay_rate"],
            domain,
            current_shop_id,
            current_shop_uuid,
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "techs": []})

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
                                WHERE (
                                        shop_uuid = %s::uuid
                                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                      )
                                    AND COALESCE(ready_to_flag, FALSE) = FALSE
                                    AND tech_id IS NOT NULL
                                GROUP BY tech_id
                        ) rc ON rc.tech_id = t.id
                        WHERE t.active = true
                          AND (
                                t.shop_uuid = %s::uuid
                             OR (t.shop_uuid IS NULL AND t.shop_id = %s AND t.domain = %s)
                              )
            ORDER BY first_name, last_name
                """, (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain))
        
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            """
            UPDATE techs
            SET status = %s
            WHERE id = %s
              AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            RETURNING id, status
            """,
                        (status_value, tech_id, current_shop_uuid, current_shop_id, domain),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            f"""
            UPDATE techs
            SET {', '.join(update_fields)}
            WHERE id = %s
              AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            RETURNING id, first_name, last_name, role, pay_rate
            """,
                        params + [tech_id, current_shop_uuid, current_shop_id, domain],
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        cur.execute(
            """
            UPDATE techs
            SET active = false
                        WHERE id = %s
                            AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            RETURNING id
            """,
                        (tech_id, current_shop_uuid, current_shop_id, domain),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT id, first_name, last_name, pay_rate
            FROM techs
            WHERE id = ANY(%s)
              AND active = TRUE
                            AND (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                            )
            ORDER BY first_name, last_name
            """,
                        (normalized_ids, current_shop_uuid, current_shop_id, domain),
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
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND tech_id = %s
                  AND tech_name IS NOT NULL
                  AND COALESCE(ready_to_flag, FALSE) = FALSE
                GROUP BY ro
                ORDER BY ro
                """,
                                (current_shop_uuid, current_shop_id, domain, tech_id),
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
                INSERT INTO archived_techs (tech_id, tech_name, pay_rate, assigned_ros, total_hours, domain, shop_id, shop_uuid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                (
                    tech_id,
                    tech_name,
                    pay_rate,
                    json.dumps(assigned_ros),
                    total_hours,
                    domain,
                    current_shop_id,
                    current_shop_uuid,
                ),
            )

            cur.execute(
                """
                UPDATE techs
                SET active = FALSE
                WHERE id = %s
                  AND (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
                """,
                (tech_id, current_shop_uuid, current_shop_id, domain),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "archived": []})
        cur.execute(
            """
            SELECT id, tech_id, tech_name, pay_rate, assigned_ros, total_hours, archived_at
            FROM archived_techs
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            ORDER BY archived_at DESC, id DESC
            """,
            (current_shop_uuid, current_shop_id, domain),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            WITH latest_estimates AS (
                SELECT DISTINCT ON (ro)
                    ro,
                    year,
                    make,
                    model,
                                        vehicle,
                                        vin,
                                        insurance_company,
                                        estimator,
                                        written_by
                FROM saved_estimates
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
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
                                le.vehicle,
                                le.vin,
                                le.insurance_company,
                                le.estimator,
                                le.written_by
            FROM ro_line_assignments a
            LEFT JOIN latest_estimates le ON le.ro = a.ro
                        WHERE (
                                        a.shop_uuid = %s::uuid
                                 OR (a.shop_uuid IS NULL AND a.shop_id = %s AND a.domain = %s)
                                    )
              AND a.tech_id = %s
              AND a.tech_name IS NOT NULL
              AND COALESCE(a.ready_to_flag, FALSE) = FALSE
                        GROUP BY a.ro, le.year, le.make, le.model, le.vehicle, le.vin, le.insurance_company, le.estimator, le.written_by
            ORDER BY ro
            """,
                        (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain, tech_id),
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
                    "vin": (row.get("vin") or "").strip(),
                    "insurance": (row.get("insurance_company") or "").strip(),
                    "estimator": (row.get("estimator") or "").strip(),
                    "written_by": (row.get("written_by") or "").strip(),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_id = %s
              AND COALESCE(ready_to_flag, FALSE) = FALSE
            ORDER BY line_number
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value, tech_id),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)

        cur.execute(
            """
            SELECT id, line_key, line_number, description, hours, tech_name, repair_type
            FROM ro_line_assignments
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_id = %s
              AND COALESCE(ready_to_flag, FALSE) = FALSE
              AND line_key = ANY(%s)
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value, tech_id, normalized_keys),
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
                    shop_id,
                    shop_uuid,
                    flagged_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ready_to_flag', %s, %s, %s::uuid, CURRENT_TIMESTAMP)
                ON CONFLICT (ro, tech_id, repair_type, line_key, domain)
                DO UPDATE SET
                    line_number = EXCLUDED.line_number,
                    description = EXCLUDED.description,
                    hours = EXCLUDED.hours,
                    pay_rate = EXCLUDED.pay_rate,
                    pay_amount = EXCLUDED.pay_amount,
                    status = 'ready_to_flag',
                    shop_id = EXCLUDED.shop_id,
                    shop_uuid = EXCLUDED.shop_uuid,
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
                    current_shop_id,
                    current_shop_uuid,
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
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND tech_id = %s
              AND repair_type = 'body'
              AND COALESCE(ready_to_flag, FALSE) = FALSE
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value, tech_id),
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
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        total_flagged_count = 0
        total_flagged_hours = 0.0
        total_flagged_pay = 0.0

        for ro_value in ro_values:
            _ensure_ro_line_assignments_for_ro(cur, domain, ro_value)
            cur.execute(
                """
                SELECT id, line_key, line_number, description, hours, tech_name, repair_type
                FROM ro_line_assignments
                                WHERE (
                                                shop_uuid = %s::uuid
                                         OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                            )
                  AND ro = %s
                  AND tech_id = %s
                  AND COALESCE(ready_to_flag, FALSE) = FALSE
                """,
                                (current_shop_uuid, current_shop_id, domain, ro_value, tech_id),
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
                        shop_id,
                        shop_uuid,
                        flagged_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ready_to_flag', %s, %s, %s::uuid, CURRENT_TIMESTAMP)
                    ON CONFLICT (ro, tech_id, repair_type, line_key, domain)
                    DO UPDATE SET
                        line_number = EXCLUDED.line_number,
                        description = EXCLUDED.description,
                        hours = EXCLUDED.hours,
                        pay_rate = EXCLUDED.pay_rate,
                        pay_amount = EXCLUDED.pay_amount,
                        status = 'ready_to_flag',
                        shop_id = EXCLUDED.shop_id,
                        shop_uuid = EXCLUDED.shop_uuid,
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
                        current_shop_id,
                        current_shop_uuid,
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





