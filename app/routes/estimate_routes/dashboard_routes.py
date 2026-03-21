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

@router.post("/flash")
async def flash_data(request: Request):
    if not get_user_domain(request):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    return JSONResponse(status_code=403, content={"error": "Endpoint disabled for tenant safety"})



@router.get("/dashboard-data")
async def get_dashboard_data(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        cur.execute(
            """
            SELECT id, first_name, last_name
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
                                     customer_phones,
                                     customer_email,
                                     in_date,
                                     ecd_date,
                                     picked_up,
                                     saved_at
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
        rows = cur.fetchall()

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

        total_sales = 0.0
        total_parts = 0.0
        total_hours = 0.0
        ro_list = []
        labor_hours_by_tech = {}
        ros_by_tech = {}
        closed_phase_keys = {"complete", "complete/finish"}

        for row in rows:
            ro = row.get("ro")
            phase_value = str(phase_map.get(ro, "teardown") or "teardown").strip().lower()
            if phase_value in closed_phase_keys:
                continue
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
            stored_phone_values = _parse_json_field(row.get("customer_phones"))
            phone_numbers = []
            if isinstance(stored_phone_values, list):
                for value in stored_phone_values:
                    phone_value = str(value or "").strip()
                    if phone_value and phone_value not in phone_numbers:
                        phone_numbers.append(phone_value)
            phone_override = (row.get("phone_override") or "").strip()
            phone_original = (row.get("phone_original") or customer_phone).strip()
            if not phone_numbers:
                fallback_phone = phone_override or customer_phone
                if fallback_phone:
                    phone_numbers.append(fallback_phone)
            current_phone = phone_numbers[0] if phone_numbers else (phone_override or customer_phone)
            customer_email = (row.get("customer_email") or "").strip()
            if not customer_email:
                email_match = re.search(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", owner_info, re.IGNORECASE)
                if email_match:
                    customer_email = (email_match.group(0) or "").strip()
            in_date_value = _coerce_date(row.get("in_date")) or _to_local_business_date(row.get("saved_at"))
            ecd_date_value = _coerce_date(row.get("ecd_date")) or _calculate_ecd_date(in_date_value, ro_hours)

            _ensure_ro_line_assignments_for_ro(
                cur,
                domain,
                ro,
                shop_id=current_shop_id,
                shop_uuid=current_shop_uuid,
            )

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
                        (current_shop_uuid, current_shop_id, domain, ro),
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
                    "phone_numbers": phone_numbers,
                    "email": customer_email,
                    "owner_info": owner_info,
                    "written_by": written_by,
                    "estimator": estimator,
                    "insurance": row.get("insurance_company") or "",
                    "claim_number": row.get("claim_number") or "",
                    "vin": row.get("vin") or "",
                    "phase": phase_value,
                    "tech": labor_tech,
                    "painter": paint_tech,
                    "in_date": in_date_value.isoformat() if in_date_value else None,
                    "ecd_date": ecd_date_value.isoformat() if ecd_date_value else None,
                    "picked_up": row.get("picked_up").isoformat() if row.get("picked_up") else None,
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





