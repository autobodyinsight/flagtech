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

@router.get("/payments/open-ros")
async def list_open_ros_for_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_phases_table(cur)
        _ensure_ro_payment_totals_table(cur)
        _ensure_ro_payment_entries_table(cur)
        _ensure_parts_received_table(cur)
        _ensure_shop_isolation_infrastructure(cur)

        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

        cur.execute(
            """
            SELECT DISTINCT ON (ro)
                   ro,
                   vehicle,
                   year,
                   make,
                   model,
                   owner_info,
                     insurance_company,
                   grand_total,
                   customer_pay,
                   insurance_pay,
                   deductible,
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
        rows = cur.fetchall() or []

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
        phase_rows = cur.fetchall() or []
        phase_map = {str(row.get("ro") or ""): str(row.get("phase") or "").strip().lower() for row in phase_rows}

        cur.execute(
            """
            SELECT ro, insurance_paid, customer_paid
            FROM ro_payment_totals
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            """,
            (current_shop_uuid, current_shop_id, domain),
        )
        payment_rows = cur.fetchall() or []
        payment_map = {
            str(payment_row.get("ro") or "").strip(): {
                "insurance_paid": _parse_float_value(payment_row.get("insurance_paid")),
                "customer_paid": _parse_float_value(payment_row.get("customer_paid")),
            }
            for payment_row in payment_rows
            if str(payment_row.get("ro") or "").strip()
        }

        cur.execute(
            """
            SELECT ro, payer_type, payment_method, check_number, created_by, amount, business_date
            FROM ro_payment_entries
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
            ORDER BY business_date DESC NULLS LAST, id DESC
            """,
            (current_shop_uuid, current_shop_id, domain),
        )
        payment_entry_rows = cur.fetchall() or []
        payment_entries_by_ro = {}
        for entry_row in payment_entry_rows:
            ro_key = str(entry_row.get("ro") or "").strip()
            payer_type = str(entry_row.get("payer_type") or "").strip().lower()
            if not ro_key or payer_type not in {"insurance", "customer"}:
                continue

            business_date = entry_row.get("business_date")
            if isinstance(business_date, datetime):
                business_date_display = business_date.date().isoformat()
            elif isinstance(business_date, date):
                business_date_display = business_date.isoformat()
            else:
                business_date_display = str(business_date or "")[:10]

            entry_bucket = payment_entries_by_ro.setdefault(ro_key, {"insurance": [], "customer": []})
            entry_bucket[payer_type].append(
                {
                    "amount": _parse_float_value(entry_row.get("amount")),
                    "business_date": business_date_display,
                    "payment_type": str(entry_row.get("payment_method") or "").strip().upper(),
                    "check_number": str(entry_row.get("check_number") or "").strip(),
                    "created_by": _resolve_note_created_by(cur, entry_row.get("created_by")),
                }
            )

        cur.execute(
            """
            SELECT
                ro,
                invoice_number,
                COALESCE(NULLIF(SUM(DISTINCT invoice_total), 0), SUM(cost), 0) AS invoice_paid_total,
                MAX(COALESCE(received_business_date, received_at::date)) AS latest_received_date
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro IS NOT NULL
              AND ro <> ''
              AND invoice_number IS NOT NULL
              AND TRIM(invoice_number) <> ''
            GROUP BY ro, invoice_number
            ORDER BY ro, latest_received_date DESC, invoice_number
            """,
            (current_shop_uuid, current_shop_id, domain),
        )
        invoice_rows = cur.fetchall() or []

        invoices_by_ro = {}
        for invoice_row in invoice_rows:
            ro_key = str(invoice_row.get("ro") or "").strip()
            invoice_number = str(invoice_row.get("invoice_number") or "").strip()
            if not ro_key or not invoice_number:
                continue
            invoices_by_ro.setdefault(ro_key, []).append(
                {
                    "invoice_number": invoice_number,
                    "amount_paid": _parse_float_value(invoice_row.get("invoice_paid_total")),
                }
            )

        payments_rows = []
        closed_phase_keys = {"complete", "complete/finish"}

        for row in rows:
            ro = str(row.get("ro") or "").strip()
            if not ro:
                continue

            phase_value = phase_map.get(ro, "teardown")
            if phase_value in closed_phase_keys:
                continue

            customer_name, _ = _parse_owner_info((row.get("owner_info") or "").strip())

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_display = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")

            grand_total = _parse_float_value(row.get("grand_total"))
            customer_total = _parse_float_value(row.get("customer_pay"))
            insurance_total = _parse_float_value(row.get("insurance_pay"))
            deductible = _parse_float_value(row.get("deductible"))

            if customer_total == 0 and deductible > 0:
                customer_total = deductible
            if insurance_total == 0 and grand_total > 0:
                insurance_total = max(0.0, grand_total - customer_total)

            paid_values = payment_map.get(ro) or {}
            insurance_paid = _parse_float_value(paid_values.get("insurance_paid"))
            customer_paid = _parse_float_value(paid_values.get("customer_paid"))
            balance = max(0.0, grand_total - insurance_paid - customer_paid)

            payments_rows.append(
                {
                    "ro": ro,
                    "customer": customer_name,
                    "insurance_name": (row.get("insurance_company") or "").strip(),
                    "vehicle": vehicle_display,
                    "insurance_total": insurance_total,
                    "customer_total": customer_total,
                    "insurance_paid": insurance_paid,
                    "customer_paid": customer_paid,
                    "grand_total": grand_total,
                    "balance": balance,
                    "invoice_payments": invoices_by_ro.get(ro, []),
                    "insurance_payment_entries": (payment_entries_by_ro.get(ro) or {}).get("insurance", []),
                    "customer_payment_entries": (payment_entries_by_ro.get(ro) or {}).get("customer", []),
                }
            )

        payments_rows.sort(key=lambda item: str(item.get("ro") or ""))
        return {"rows": payments_rows}
    finally:
        cur.close()



@router.get("/payments/ro")
async def get_ro_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    ro_value = str(request.query_params.get("ro") or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_payment_totals_table(cur)
        _ensure_ro_payment_entries_table(cur)
        _ensure_shop_isolation_infrastructure(cur)

        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
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
                   owner_info,
                   insurance_company,
                   grand_total,
                   customer_pay,
                   insurance_pay,
                   deductible,
                   saved_at
            FROM saved_estimates
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            ORDER BY ro, saved_at DESC, id DESC
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        cur.execute(
            """
            SELECT insurance_paid, customer_paid
            FROM ro_payment_totals
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            LIMIT 1
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        totals_row = cur.fetchone() or {}

        cur.execute(
            """
            SELECT ro, payer_type, payment_method, check_number, created_by, amount, business_date
            FROM ro_payment_entries
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            ORDER BY business_date DESC NULLS LAST, id DESC
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        payment_entry_rows = cur.fetchall() or []

        payment_entries = {"insurance": [], "customer": []}
        for entry_row in payment_entry_rows:
            payer_type = str(entry_row.get("payer_type") or "").strip().lower()
            if payer_type not in {"insurance", "customer"}:
                continue

            business_date = entry_row.get("business_date")
            if isinstance(business_date, datetime):
                business_date_display = business_date.date().isoformat()
            elif isinstance(business_date, date):
                business_date_display = business_date.isoformat()
            else:
                business_date_display = str(business_date or "")[:10]

            payment_entries[payer_type].append(
                {
                    "amount": _parse_float_value(entry_row.get("amount")),
                    "business_date": business_date_display,
                    "payment_type": str(entry_row.get("payment_method") or "").strip().upper(),
                    "check_number": str(entry_row.get("check_number") or "").strip(),
                    "created_by": _resolve_note_created_by(cur, entry_row.get("created_by")),
                }
            )

        customer_name, _ = _parse_owner_info((row.get("owner_info") or "").strip())

        year = (row.get("year") or "").strip()
        make = (row.get("make") or "").strip()
        model = (row.get("model") or "").strip()
        vehicle_display = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")

        grand_total = _parse_float_value(row.get("grand_total"))
        customer_total = _parse_float_value(row.get("customer_pay"))
        insurance_total = _parse_float_value(row.get("insurance_pay"))
        deductible = _parse_float_value(row.get("deductible"))

        if customer_total == 0 and deductible > 0:
            customer_total = deductible
        if insurance_total == 0 and grand_total > 0:
            insurance_total = max(0.0, grand_total - customer_total)

        insurance_paid = _parse_float_value(totals_row.get("insurance_paid"))
        customer_paid = _parse_float_value(totals_row.get("customer_paid"))
        balance = max(0.0, grand_total - insurance_paid - customer_paid)

        return {
            "row": {
                "ro": ro_value,
                "customer": customer_name,
                "insurance_name": (row.get("insurance_company") or "").strip(),
                "vehicle": vehicle_display,
                "insurance_total": insurance_total,
                "customer_total": customer_total,
                "insurance_paid": insurance_paid,
                "customer_paid": customer_paid,
                "grand_total": grand_total,
                "balance": balance,
                "insurance_payment_entries": payment_entries.get("insurance", []),
                "customer_payment_entries": payment_entries.get("customer", []),
            }
        }
    finally:
        cur.close()



@router.get("/records/closed-ros")
async def list_records_closed_ros(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_phases_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

        cur.execute(
            """
            SELECT
                rp.ro,
                rp.updated_at,
                se.year,
                se.make,
                se.model,
                se.vehicle,
                se.owner_info,
                se.insurance_company,
                se.in_date,
                se.picked_up,
                se.grand_total
            FROM ro_phases rp
            LEFT JOIN LATERAL (
                SELECT *
                FROM saved_estimates se
                WHERE se.ro = rp.ro
                                    AND (
                                                se.shop_uuid = %s::uuid
                                         OR (se.shop_uuid IS NULL AND se.shop_id = %s AND se.domain = %s)
                                    )
                ORDER BY se.saved_at DESC, se.id DESC
                LIMIT 1
            ) se ON TRUE
                        WHERE (
                                        rp.shop_uuid = %s::uuid
                                 OR (rp.shop_uuid IS NULL AND rp.shop_id = %s AND rp.domain = %s)
                                    )
              AND COALESCE(LOWER(TRIM(rp.phase)), '') IN ('complete', 'complete/finish')
            ORDER BY rp.updated_at DESC NULLS LAST, rp.ro ASC
            """,
                        (current_shop_uuid, current_shop_id, domain, current_shop_uuid, current_shop_id, domain),
        )
        rows = cur.fetchall() or []

        records_rows = []
        for row in rows:
            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_value = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")
            customer_name, _ = _parse_owner_info((row.get("owner_info") or "").strip())

            in_date_value = _coerce_date(row.get("in_date"))
            out_date_value = _coerce_date(row.get("picked_up"))
            closed_raw = row.get("updated_at")
            closed_date_value = closed_raw if isinstance(closed_raw, datetime) else None

            records_rows.append(
                {
                    "ro": str(row.get("ro") or "").strip(),
                    "vehicle": vehicle_value,
                    "customer": customer_name,
                    "insurance": (row.get("insurance_company") or "").strip(),
                    "in_date": in_date_value.isoformat() if in_date_value else None,
                    "out_date": out_date_value.isoformat() if out_date_value else None,
                    "closed_date": closed_date_value.isoformat() if closed_date_value else None,
                    "total": _parse_float_value(row.get("grand_total")),
                }
            )

        return {"rows": records_rows}
    finally:
        cur.close()



@router.get("/records/tech-payouts")
async def list_records_tech_payouts(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Return per-tech payout totals from paid Flagout entries."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    start_date_value = None
    if start_date:
        try:
            start_date_value = date.fromisoformat(str(start_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "start_date must be YYYY-MM-DD", "rows": []})

    end_date_value = None
    if end_date:
        try:
            end_date_value = date.fromisoformat(str(end_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "end_date must be YYYY-MM-DD", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

        cur.execute(
            """
            WITH paid_lines AS (
                SELECT
                    f.id,
                    f.tech_id,
                    f.tech_name,
                    f.pay_rate,
                    f.ro,
                    f.hours,
                    f.paid_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY f.tech_id
                        ORDER BY f.paid_at DESC NULLS LAST, f.id DESC
                    ) AS row_rank
                FROM ro_flagout_lines f
                                WHERE (
                                                f.shop_uuid = %s::uuid
                                         OR (f.shop_uuid IS NULL AND f.shop_id = %s AND f.domain = %s)
                                    )
                  AND f.tech_id IS NOT NULL
                  AND f.paid_at IS NOT NULL
                                    AND (%s::date IS NULL OR f.paid_at::date >= %s::date)
                                    AND (%s::date IS NULL OR f.paid_at::date <= %s::date)
            ),
            aggregates AS (
                SELECT
                    tech_id,
                    COALESCE(SUM(hours), 0) AS total_hours,
                    COUNT(DISTINCT NULLIF(TRIM(ro), '')) AS total_ros
                FROM paid_lines
                GROUP BY tech_id
            )
            SELECT
                a.tech_id,
                COALESCE(NULLIF(TRIM(p.tech_name), ''), CONCAT('Tech #', a.tech_id::text)) AS tech_name,
                COALESCE(p.pay_rate, 0) AS pay_rate,
                a.total_hours,
                a.total_ros
            FROM aggregates a
            LEFT JOIN paid_lines p
              ON p.tech_id = a.tech_id
             AND p.row_rank = 1
            ORDER BY tech_name ASC
            """,
                        (current_shop_uuid, current_shop_id, domain, start_date_value, start_date_value, end_date_value, end_date_value),
        )
        rows = cur.fetchall() or []

        payout_rows = []
        for row in rows:
            payout_rows.append(
                {
                    "tech_id": int(row.get("tech_id") or 0),
                    "tech_name": str(row.get("tech_name") or "").strip(),
                    "pay_rate": _parse_float_value(row.get("pay_rate")),
                    "total_hours": _parse_float_value(row.get("total_hours")),
                    "total_ros": int(row.get("total_ros") or 0),
                }
            )

        return {"rows": payout_rows}
    finally:
        cur.close()



@router.get("/records/tech-paid-ros")
async def list_records_tech_paid_ros(
    request: Request,
    tech_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Return unique ROs paid to a tech, sourced only from Flagout payout records."""
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    start_date_value = None
    if start_date:
        try:
            start_date_value = date.fromisoformat(str(start_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "start_date must be YYYY-MM-DD", "rows": []})

    end_date_value = None
    if end_date:
        try:
            end_date_value = date.fromisoformat(str(end_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "end_date must be YYYY-MM-DD", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)
        _ensure_saved_estimates_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

        cur.execute(
            """
            WITH paid_ro_hours AS (
                SELECT
                    f.tech_id,
                    f.ro,
                    COALESCE(SUM(f.hours), 0) AS total_hours,
                    COALESCE(SUM(COALESCE(f.pay_amount, COALESCE(f.hours, 0) * COALESCE(f.pay_rate, 0))), 0) AS total_paid,
                    MAX(f.paid_at) AS paid_at
                FROM ro_flagout_lines f
                                WHERE (
                                                f.shop_uuid = %s::uuid
                                         OR (f.shop_uuid IS NULL AND f.shop_id = %s AND f.domain = %s)
                                    )
                  AND f.paid_at IS NOT NULL
                  AND f.tech_id = %s
                                    AND (%s::date IS NULL OR f.paid_at::date >= %s::date)
                                    AND (%s::date IS NULL OR f.paid_at::date <= %s::date)
                  AND f.ro IS NOT NULL
                  AND TRIM(f.ro) <> ''
                GROUP BY f.tech_id, f.ro
            ),
            latest_estimates AS (
                SELECT DISTINCT ON (se.ro)
                    se.ro,
                    se.vehicle,
                    se.year,
                    se.make,
                    se.model,
                    se.insurance_company,
                    se.in_date,
                    se.ecd_date,
                    se.grand_total,
                    se.saved_at
                FROM saved_estimates se
                                WHERE (
                                                se.shop_uuid = %s::uuid
                                         OR (se.shop_uuid IS NULL AND se.shop_id = %s AND se.domain = %s)
                                    )
                ORDER BY se.ro, se.saved_at DESC, se.id DESC
            )
            SELECT
                p.tech_id,
                p.ro,
                p.total_hours,
                p.total_paid,
                p.paid_at,
                le.vehicle,
                le.year,
                le.make,
                le.model,
                le.insurance_company,
                le.in_date,
                le.ecd_date,
                le.grand_total,
                le.saved_at
            FROM paid_ro_hours p
            LEFT JOIN latest_estimates le ON le.ro = p.ro
            ORDER BY p.ro ASC
            """,
            (current_shop_uuid, current_shop_id, domain, tech_id, start_date_value, start_date_value, end_date_value, end_date_value, current_shop_uuid, current_shop_id, domain),
        )
        rows = cur.fetchall() or []

        ros = []
        for row in rows:
            ro_value = str(row.get("ro") or "").strip()
            if not ro_value:
                continue

            year = (row.get("year") or "").strip()
            make = (row.get("make") or "").strip()
            model = (row.get("model") or "").strip()
            vehicle_display = " ".join(part for part in (year, make, model) if part) or (row.get("vehicle") or "")

            in_date_value = _coerce_date(row.get("in_date")) or _to_local_business_date(row.get("saved_at"))
            ecd_date_value = _coerce_date(row.get("ecd_date")) or _calculate_ecd_date(
                in_date_value,
                _parse_float_value(row.get("total_hours")),
            )

            ros.append(
                {
                    "tech_id": int(row.get("tech_id") or 0),
                    "ro": ro_value,
                    "vehicle": str(vehicle_display or "").strip(),
                    "insurance": str(row.get("insurance_company") or "").strip(),
                    "paid_at": row.get("paid_at").isoformat() if row.get("paid_at") else None,
                    "in_date": in_date_value.isoformat() if in_date_value else None,
                    "ecd_date": ecd_date_value.isoformat() if ecd_date_value else None,
                    "hours": _parse_float_value(row.get("total_hours")),
                    "total": _parse_float_value(row.get("total_paid")),
                }
            )

        return {"rows": ros}
    finally:
        cur.close()



@router.get("/records/parts/vendors-summary")
async def list_records_parts_vendors_summary(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    start_date_value = None
    if start_date:
        try:
            start_date_value = date.fromisoformat(str(start_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "start_date must be YYYY-MM-DD", "rows": []})

    end_date_value = None
    if end_date:
        try:
            end_date_value = date.fromisoformat(str(end_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "end_date must be YYYY-MM-DD", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        _ensure_parts_received_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

        cur.execute(
            """
            SELECT
                v.id,
                v.name,
                v.vendor_type,
                COALESCE(
                    COUNT(
                        DISTINCT CASE
                            WHEN pr.invoice_number IS NOT NULL AND TRIM(pr.invoice_number) <> ''
                            THEN CONCAT(COALESCE(pr.ro, ''), '|', TRIM(pr.invoice_number))
                            ELSE NULL
                        END
                    ),
                    0
                ) AS invoice_count,
                COALESCE(
                    SUM(
                        CASE
                            WHEN pr.invoice_number IS NOT NULL AND TRIM(pr.invoice_number) <> ''
                            THEN COALESCE(pr.cost, 0)
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_cost
            FROM parts_vendors v
            LEFT JOIN parts_received pr
                     ON LOWER(TRIM(pr.vendor)) = LOWER(TRIM(v.name))
                    AND (
                        pr.shop_uuid = %s::uuid
                       OR (pr.shop_uuid IS NULL AND pr.shop_id = %s AND pr.domain = %s)
                    )
                                    AND (%s::date IS NULL OR COALESCE(pr.received_business_date, pr.received_at::date) >= %s::date)
                                    AND (%s::date IS NULL OR COALESCE(pr.received_business_date, pr.received_at::date) <= %s::date)
                WHERE (
                      v.shop_uuid = %s::uuid
                     OR (v.shop_uuid IS NULL AND v.shop_id = %s AND v.domain = %s)
                    )
              AND v.active = TRUE
            GROUP BY v.id, v.name, v.vendor_type
            ORDER BY LOWER(TRIM(v.name)) ASC
            """,
                (current_shop_uuid, current_shop_id, domain, start_date_value, start_date_value, end_date_value, end_date_value, current_shop_uuid, current_shop_id, domain),
        )
        rows = cur.fetchall() or []

        data_rows = []
        for row in rows:
            data_rows.append(
                {
                    "vendor_id": int(row.get("id") or 0),
                    "vendor": str(row.get("name") or "").strip(),
                    "type": str(row.get("vendor_type") or "").strip(),
                    "invoices": int(row.get("invoice_count") or 0),
                    "total": _parse_float_value(row.get("total_cost")),
                }
            )

        return {"rows": data_rows}
    finally:
        cur.close()



@router.get("/records/parts/vendor-invoices")
async def list_records_parts_vendor_invoices(
    request: Request,
    vendor_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "rows": []})

    start_date_value = None
    if start_date:
        try:
            start_date_value = date.fromisoformat(str(start_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "start_date must be YYYY-MM-DD", "rows": []})

    end_date_value = None
    if end_date:
        try:
            end_date_value = date.fromisoformat(str(end_date).strip()[:10])
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "end_date must be YYYY-MM-DD", "rows": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        _ensure_parts_received_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "rows": []})

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
            return JSONResponse(status_code=404, content={"error": "Vendor not found", "rows": []})

        vendor_name = str(vendor_row.get("name") or "").strip()
        if not vendor_name:
            return {"rows": []}

        cur.execute(
            """
            SELECT
                pr.ro,
                TRIM(pr.invoice_number) AS invoice_number,
                MAX(COALESCE(pr.received_business_date, pr.received_at::date)) AS invoice_date,
                COUNT(*) AS parts_count,
                COALESCE(SUM(pr.cost), 0) AS total_cost
            FROM parts_received pr
                        WHERE (
                                        pr.shop_uuid = %s::uuid
                                 OR (pr.shop_uuid IS NULL AND pr.shop_id = %s AND pr.domain = %s)
                                    )
              AND LOWER(TRIM(pr.vendor)) = LOWER(TRIM(%s))
              AND pr.invoice_number IS NOT NULL
              AND TRIM(pr.invoice_number) <> ''
              AND (%s IS NULL OR COALESCE(pr.received_business_date, pr.received_at::date) >= %s)
              AND (%s IS NULL OR COALESCE(pr.received_business_date, pr.received_at::date) <= %s)
            GROUP BY pr.ro, TRIM(pr.invoice_number)
            ORDER BY MAX(COALESCE(pr.received_business_date, pr.received_at::date)) DESC, pr.ro ASC, TRIM(pr.invoice_number) ASC
            """,
                        (current_shop_uuid, current_shop_id, domain, vendor_name, start_date_value, start_date_value, end_date_value, end_date_value),
        )
        rows = cur.fetchall() or []

        data_rows = []
        for row in rows:
            invoice_date = row.get("invoice_date")
            data_rows.append(
                {
                    "date": invoice_date.isoformat() if invoice_date else None,
                    "ro": str(row.get("ro") or "").strip(),
                    "invoice": str(row.get("invoice_number") or "").strip(),
                    "parts": int(row.get("parts_count") or 0),
                    "total": _parse_float_value(row.get("total_cost")),
                }
            )

        return {"rows": data_rows}
    finally:
        cur.close()



@router.get("/records/parts/vendor-invoice-parts")
async def list_records_parts_vendor_invoice_parts(request: Request, vendor_id: int, ro: str, invoice: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "parts": []})
    ro_value = str(ro or "").strip()
    invoice_value = str(invoice or "").strip()

    if not ro_value or not invoice_value:
        return JSONResponse(status_code=400, content={"error": "ro and invoice are required", "parts": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_parts_vendors_table(cur)
        _ensure_parts_received_table(cur)
        _ensure_saved_estimates_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
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

        vendor_name = str(vendor_row.get("name") or "").strip()
        if not vendor_name:
            return {"parts": []}

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
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        estimate_row = cur.fetchone() or {}
        parts_repairs = _parse_json_field(estimate_row.get("parts_repairs"))
        if not isinstance(parts_repairs, list):
            parts_repairs = []

        line_lookup = {}
        for idx, item in enumerate(parts_repairs, start=1):
            if not isinstance(item, dict):
                continue
            parsed_description, parsed_part_number = _parse_part_description_and_number(item)
            line_lookup[idx] = {
                "line": item.get("line") or idx,
                "description": parsed_description,
                "part_number": parsed_part_number or "",
                "qty": _parse_float_value(item.get("qty")),
                "list": _parse_float_value(item.get("price")),
            }

        cur.execute(
            """
            SELECT
                line_id,
                description,
                part_number,
                qty_received,
                list_price,
                cost
            FROM parts_received
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
              AND TRIM(invoice_number) = %s
              AND LOWER(TRIM(vendor)) = LOWER(TRIM(%s))
            ORDER BY line_id
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value, invoice_value, vendor_name),
        )
        rows = cur.fetchall() or []

        parts = []
        for row in rows:
            try:
                line_id = int(row.get("line_id") or 0)
            except Exception:
                line_id = 0
            lookup = line_lookup.get(line_id, {})
            parts.append(
                {
                    "line": lookup.get("line") or line_id,
                    "description": (row.get("description") or lookup.get("description") or "").strip(),
                    "qty": _parse_float_value(row.get("qty_received")) or _parse_float_value(lookup.get("qty")) or 0.0,
                    "part_number": (row.get("part_number") or lookup.get("part_number") or "").strip(),
                    "list": _parse_float_value(row.get("list_price")) or _parse_float_value(lookup.get("list")),
                    "cost": _parse_float_value(row.get("cost")),
                }
            )

        return {"parts": parts}
    finally:
        cur.close()



@router.post("/payments/save")
async def save_ro_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    data = await request.json()
    ro_value = str(data.get("ro") or "").strip()

    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})

    insurance_paid_raw = data.get("insurance_paid", 0)
    customer_paid_raw = data.get("customer_paid", 0)
    insurance_payment_raw = data.get("insurance_payment", None)
    customer_payment_raw = data.get("customer_payment", None)
    insurance_payment_type_raw = str(data.get("insurance_payment_type") or "").strip().upper()
    customer_payment_type_raw = str(data.get("customer_payment_type") or "").strip().upper()
    insurance_check_number_raw = str(data.get("insurance_check_number") or "").strip()
    customer_check_number_raw = str(data.get("customer_check_number") or "").strip()
    business_date_raw = str(data.get("business_date") or "").strip()
    has_incremental_values = insurance_payment_raw is not None or customer_payment_raw is not None

    allowed_payment_types = {"CARD", "CASH", "CHECK"}
    insurance_payment_type = insurance_payment_type_raw if insurance_payment_type_raw in allowed_payment_types else ""
    customer_payment_type = customer_payment_type_raw if customer_payment_type_raw in allowed_payment_types else ""

    def _parse_payment_amount(raw_value) -> float:
        cleaned = str(raw_value if raw_value is not None else "").replace("$", "").replace(",", "").strip()
        if cleaned == "":
            return 0.0
        parsed = float(cleaned)
        if not math.isfinite(parsed):
            raise ValueError("amount must be finite")
        return parsed

    try:
        insurance_paid = _parse_payment_amount(insurance_paid_raw)
        customer_paid = _parse_payment_amount(customer_paid_raw)
    except (TypeError, ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": "insurance_paid and customer_paid must be valid currency values"},
        )

    if insurance_paid < 0 or customer_paid < 0:
        return JSONResponse(status_code=400, content={"error": "payment amounts cannot be negative"})

    business_date_value = None
    if business_date_raw:
        raw_date = business_date_raw[:10]
        try:
            business_date_value = date.fromisoformat(raw_date)
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "business_date must be YYYY-MM-DD"})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_saved_estimates_table(cur)
        _ensure_ro_payment_totals_table(cur)
        _ensure_ro_payment_entries_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
        created_by = _resolve_request_user_display_name(request, cur, domain)

        cur.execute(
            """
            SELECT grand_total
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
        ro_row = cur.fetchone()
        if not ro_row:
            return JSONResponse(status_code=404, content={"error": "RO not found"})

        grand_total = _parse_float_value(ro_row.get("grand_total"))

        cur.execute(
            """
            SELECT insurance_paid, customer_paid
            FROM ro_payment_totals
                        WHERE (
                                        shop_uuid = %s::uuid
                                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                                    )
              AND ro = %s
            LIMIT 1
            """,
                        (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        existing_row = cur.fetchone() or {}
        existing_insurance_paid = _parse_float_value(existing_row.get("insurance_paid"))
        existing_customer_paid = _parse_float_value(existing_row.get("customer_paid"))

        insurance_entry_amount = 0.0
        customer_entry_amount = 0.0

        if has_incremental_values:
            try:
                insurance_entry_amount = _parse_payment_amount(insurance_payment_raw)
                customer_entry_amount = _parse_payment_amount(customer_payment_raw)
            except (TypeError, ValueError):
                return JSONResponse(
                    status_code=400,
                    content={"error": "insurance_payment and customer_payment must be valid currency values"},
                )

            if insurance_entry_amount < 0 or customer_entry_amount < 0:
                return JSONResponse(status_code=400, content={"error": "payment amounts cannot be negative"})

            insurance_paid = existing_insurance_paid + insurance_entry_amount
            customer_paid = existing_customer_paid + customer_entry_amount

        cur.execute(
            """
            INSERT INTO ro_payment_totals (ro, domain, shop_id, shop_uuid, insurance_paid, customer_paid, updated_at)
            VALUES (%s, %s, %s, %s::uuid, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (domain, ro)
            DO UPDATE SET
                shop_id = EXCLUDED.shop_id,
                shop_uuid = EXCLUDED.shop_uuid,
                insurance_paid = EXCLUDED.insurance_paid,
                customer_paid = EXCLUDED.customer_paid,
                updated_at = CURRENT_TIMESTAMP
            """,
            (ro_value, domain, current_shop_id, current_shop_uuid, insurance_paid, customer_paid),
        )

        if insurance_entry_amount > 0:
            insurance_check_number = insurance_check_number_raw if insurance_payment_type == "CHECK" else ""
            cur.execute(
                """
                INSERT INTO ro_payment_entries (
                    ro,
                    domain,
                    shop_id,
                    shop_uuid,
                    payer_type,
                    payment_method,
                    check_number,
                    created_by,
                    amount,
                    business_date,
                    created_at
                )
                VALUES (%s, %s, %s, %s::uuid, 'insurance', %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    ro_value,
                    domain,
                    current_shop_id,
                    current_shop_uuid,
                    insurance_payment_type or None,
                    insurance_check_number or None,
                    created_by,
                    insurance_entry_amount,
                    business_date_value,
                ),
            )

        if customer_entry_amount > 0:
            customer_check_number = customer_check_number_raw if customer_payment_type == "CHECK" else ""
            cur.execute(
                """
                INSERT INTO ro_payment_entries (
                    ro,
                    domain,
                    shop_id,
                    shop_uuid,
                    payer_type,
                    payment_method,
                    check_number,
                    created_by,
                    amount,
                    business_date,
                    created_at
                )
                VALUES (%s, %s, %s, %s::uuid, 'customer', %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    ro_value,
                    domain,
                    current_shop_id,
                    current_shop_uuid,
                    customer_payment_type or None,
                    customer_check_number or None,
                    created_by,
                    customer_entry_amount,
                    business_date_value,
                ),
            )

        conn.commit()

        balance = max(0.0, grand_total - insurance_paid - customer_paid)
        return {
            "status": "success",
            "ro": ro_value,
            "insurance_paid": insurance_paid,
            "customer_paid": customer_paid,
            "insurance_payment_saved": insurance_entry_amount,
            "customer_payment_saved": customer_entry_amount,
            "grand_total": grand_total,
            "balance": balance,
        }
    finally:
        cur.close()



@router.post("/payments/close-ro")
async def close_ro_from_payments(request: Request):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    try:
        data = await request.json()
    except Exception:
        data = {}
    ro_value = str(data.get("ro") or "").strip()

    conn = get_conn()
    cur = conn.cursor()
    previous_autocommit = conn.autocommit

    try:
        conn.autocommit = False

        _ensure_saved_estimates_table(cur)
        _ensure_ro_phases_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            conn.rollback()
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})

        if ro_value:
            cur.execute(
                """
                SELECT 1
                FROM saved_estimates
                WHERE ro = %s
                  AND (
                        shop_uuid = %s::uuid
                     OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
                LIMIT 1
                """,
                (ro_value, current_shop_uuid, current_shop_id, domain),
            )
            if not cur.fetchone():
                conn.rollback()
                return JSONResponse(status_code=404, content={"error": "RO not found for current tenant"})

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
                (ro_value, "complete/finish", domain, current_shop_id, current_shop_uuid),
            )

        conn.commit()
        return {
            "status": "success",
            "ro": ro_value,
            "phase": "complete/finish",
        }
    except Exception as exc:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        conn.autocommit = previous_autocommit
        cur.close()



@router.get("/payments/log")
async def get_ro_payment_log(request: Request, ro: str):
    domain = get_user_domain(request)
    if not domain:
        return JSONResponse(status_code=401, content={"error": "Not authenticated", "entries": []})

    ro_value = (ro or "").strip()
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required", "entries": []})

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_ro_flagout_lines_table(cur)
        _ensure_shop_isolation_infrastructure(cur)
        current_shop_id = _resolve_request_shop_id(request, cur, domain)
        current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
        if not current_shop_id or not current_shop_uuid:
            return JSONResponse(status_code=403, content={"error": "Shop scope not resolved", "entries": []})

        cur.execute(
            """
            SELECT
                paid_at,
                COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned') AS tech_name,
                COALESCE(SUM(pay_amount), 0) AS amount
            FROM ro_flagout_lines
            WHERE (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
                  )
              AND ro = %s
              AND paid_at IS NOT NULL
            GROUP BY paid_at, COALESCE(NULLIF(TRIM(tech_name), ''), 'Unassigned')
            ORDER BY paid_at DESC, tech_name ASC
            """,
            (current_shop_uuid, current_shop_id, domain, ro_value),
        )
        rows = cur.fetchall() or []

        entries = []
        for row in rows:
            paid_at = row.get("paid_at")
            if isinstance(paid_at, datetime):
                paid_display = paid_at.strftime("%Y-%m-%d %I:%M %p")
            elif isinstance(paid_at, date):
                paid_display = paid_at.isoformat()
            else:
                paid_display = str(paid_at or "")

            entries.append(
                {
                    "paid_at": paid_display,
                    "tech_name": row.get("tech_name") or "Unassigned",
                    "amount": _parse_float_value(row.get("amount")),
                }
            )

        return {"entries": entries}
    finally:
        cur.close()





