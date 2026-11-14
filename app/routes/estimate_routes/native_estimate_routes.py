"""Native estimating API.

Saves an original estimate, prices it in cents, and converts it into the same
saved_estimates repair-order record the CCC/Mitchell import already uses.
"""

from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.routes.estimate_modules.shop_scope import resolve_request_scope
from app.services.audit import write_audit
from app.services.db import get_conn
from app.services.duplicates import query_duplicate_matches
from app.services.estimate_math import OPERATIONS, to_repair_order_documents, total_lines
from app.services.middleware import get_authenticated_user
from app.services.parts_catalog import get_parts_catalog
from app.services.pdf_export import render_text_pdf
from app.services.permissions import snapshot_can_view_financials
from app.services.vehicle_diagram import area_catalog, normalize_body_style, render_area_svg, render_vehicle_svg
from app.services.vin import decode_vin

router = APIRouter()


def _scope_or_response(request: Request, cur):
    user = get_authenticated_user(request)
    if not user:
        return None, JSONResponse(status_code=401, content={"error": "Not authenticated"})
    scope = resolve_request_scope(request, cur, domain=user.get("domain"))
    if not scope.get("shop_id") or not scope.get("shop_uuid"):
        return None, JSONResponse(status_code=403, content={"error": "Shop scope not resolved"})
    scope["user"] = user
    return scope, None


def _rates_from_row(row: dict | None) -> dict:
    row = row or {}
    return {
        "body_rate_cents": int(row.get("body_rate_cents") or 0),
        "refinish_rate_cents": int(row.get("refinish_rate_cents") or 0),
        "mechanical_rate_cents": int(row.get("mechanical_rate_cents") or 0),
        "frame_rate_cents": int(row.get("frame_rate_cents") or 0),
        "paint_materials_per_hour_cents": int(row.get("paint_materials_per_hour_cents") or 0),
    }


def _load_rates(cur, scope) -> dict:
    cur.execute(
        """
        SELECT body_rate_cents, refinish_rate_cents, mechanical_rate_cents,
               frame_rate_cents, paint_materials_per_hour_cents
        FROM shop_labor_rates
        WHERE domain = %s
        LIMIT 1
        """,
        (scope["domain"],),
    )
    return _rates_from_row(cur.fetchone() or {})


def _public_estimate(row: dict) -> dict:
    def _json(value, fallback):
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return fallback
        return fallback

    return {
        "id": str(row.get("public_id") or ""),
        "estimate_number": row.get("estimate_number"),
        "version": int(row.get("version") or 1),
        "supplement_number": int(row.get("supplement_number") or 0),
        "parent_id": str(row.get("parent_public_id") or "") or None,
        "status": row.get("status") or "draft",
        "ro": row.get("ro") or "",
        "customer": _json(row.get("customer"), {}),
        "vehicle": _json(row.get("vehicle"), {}),
        "vin": row.get("vin") or "",
        "lines": _json(row.get("lines"), []),
        "totals": _json(row.get("totals"), {}),
        "rates": _json(row.get("rates"), {}),
        "notes": _json(row.get("notes"), []),
    }


def _load_estimate(cur, scope, public_id: str):
    cur.execute(
        """
        SELECT *
        FROM native_estimates
        WHERE public_id = %s::uuid
          AND deleted_at IS NULL
          AND (
                shop_uuid = %s::uuid
             OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
          )
        LIMIT 1
        """,
        (public_id, scope["shop_uuid"], scope["shop_id"], scope["domain"]),
    )
    return cur.fetchone()


def _allocate_ro(cur, domain: str) -> str:
    cur.execute("CREATE SEQUENCE IF NOT EXISTS ro_auto_counter_seq START WITH 12365 MINVALUE 12365")
    cur.execute(
        """
        SELECT COALESCE(MAX(CAST(SUBSTRING(ro FROM 3 FOR 5) AS INTEGER)), 0) AS max_saved
        FROM saved_estimates
        WHERE ro ~ '^AB[0-9]{5}$'
          AND domain = %s
        """,
        (domain,),
    )
    row = cur.fetchone() or {}
    floor = max(12364, int(row.get("max_saved") or 0))
    cur.execute("SELECT last_value FROM ro_auto_counter_seq")
    seq_row = cur.fetchone() or {}
    if floor > int(seq_row.get("last_value") or 0):
        cur.execute("SELECT setval('ro_auto_counter_seq', %s, true)", (floor,))
    while True:
        cur.execute("SELECT nextval('ro_auto_counter_seq') AS next_value")
        nxt = int((cur.fetchone() or {}).get("next_value") or 12365)
        candidate = f"AB{nxt:05d}"
        cur.execute(
            "SELECT 1 FROM saved_estimates WHERE domain = %s AND ro = %s LIMIT 1",
            (domain, candidate),
        )
        if cur.fetchone() is None:
            return candidate


@router.post("/native-estimates/decode-vin")
async def native_decode_vin(request: Request):
    data = await request.json()
    decoded = decode_vin(data.get("vin"))
    status = 200 if decoded.get("decoded") or decoded["validation"]["valid_format"] else 400
    if decoded["validation"]["errors"] and not decoded.get("decoded"):
        status = 400
    return JSONResponse(status_code=status, content=decoded)


@router.get("/catalog/areas")
async def catalog_areas(body_style: str = "sedan", doors: int = 4):
    style = normalize_body_style(body_style, doors)
    return {"body_style": style, "doors": 2 if style == "coupe" else doors, "areas": area_catalog(style, doors)}


@router.get("/catalog/diagram")
async def catalog_diagram(body_style: str = "sedan", doors: int = 4, side: str = "left", selected: str = ""):
    svg = render_vehicle_svg(body_style, doors, side, selected)
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/catalog/area-diagram")
async def catalog_area_diagram(area: str = "front_bumper"):
    return Response(content=render_area_svg(area), media_type="image/svg+xml")


@router.get("/catalog/parts")
async def catalog_parts(request: Request, area: str = "", body_style: str = "", vin: str = "", year: str = "", make: str = "", model: str = ""):
    catalog = get_parts_catalog()
    return {
        "provider": catalog.name,
        "licensed": catalog.licensed,
        "notice": "Mock data only. Vehicle-specific MOTOR and OEM catalogs require a license.",
        "parts": catalog.lookup(area=area, body_style=body_style, vin=vin, year=year, make=make, model=model),
    }


@router.get("/shop/labor-rates")
async def get_labor_rates(request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        return {"rates": _load_rates(cur, scope)}
    finally:
        cur.close()


@router.post("/shop/labor-rates")
async def save_labor_rates(request: Request):
    data = await request.json()
    cleaned = {}
    for key in (
        "body_rate_cents",
        "refinish_rate_cents",
        "mechanical_rate_cents",
        "frame_rate_cents",
        "paint_materials_per_hour_cents",
    ):
        try:
            cleaned[key] = max(0, int(data.get(key) or 0))
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": f"{key} must be cents"})
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        cur.execute(
            """
            INSERT INTO shop_labor_rates (
                domain, shop_id, shop_uuid, body_rate_cents, refinish_rate_cents,
                mechanical_rate_cents, frame_rate_cents, paint_materials_per_hour_cents, updated_at
            )
            VALUES (%s, %s, %s::uuid, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (domain) DO UPDATE SET
                shop_id = EXCLUDED.shop_id,
                shop_uuid = EXCLUDED.shop_uuid,
                body_rate_cents = EXCLUDED.body_rate_cents,
                refinish_rate_cents = EXCLUDED.refinish_rate_cents,
                mechanical_rate_cents = EXCLUDED.mechanical_rate_cents,
                frame_rate_cents = EXCLUDED.frame_rate_cents,
                paint_materials_per_hour_cents = EXCLUDED.paint_materials_per_hour_cents,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                scope["domain"],
                scope["shop_id"],
                scope["shop_uuid"],
                cleaned["body_rate_cents"],
                cleaned["refinish_rate_cents"],
                cleaned["mechanical_rate_cents"],
                cleaned["frame_rate_cents"],
                cleaned["paint_materials_per_hour_cents"],
            ),
        )
        user = scope["user"]
        write_audit(
            cur,
            domain=scope["domain"],
            shop_id=scope["shop_id"],
            actor_user_id=user.get("id"),
            actor_email=user.get("email"),
            action="update",
            entity_type="labor_rates",
            entity_id=scope["domain"],
            after=cleaned,
        )
        conn.commit()
        return {"status": "ok", "rates": cleaned}
    finally:
        cur.close()


def _payload_from_body(data: dict, rates: dict) -> tuple[dict | None, str | None]:
    customer = data.get("customer") if isinstance(data.get("customer"), dict) else {}
    vehicle = data.get("vehicle") if isinstance(data.get("vehicle"), dict) else {}
    lines = data.get("lines") if isinstance(data.get("lines"), list) else []
    if len(lines) > 400:
        return None, "Too many estimate lines"
    for line in lines:
        if str(line.get("operation") or "Repair") not in OPERATIONS and line.get("operation"):
            return None, "Unknown operation"
    try:
        deductible = max(0, int(data.get("deductible_cents") or 0))
    except (TypeError, ValueError):
        return None, "deductible_cents must be an integer"
    summary = total_lines(lines, rates, deductible)
    notes = data.get("notes") if isinstance(data.get("notes"), list) else []
    clean_notes = [str(note)[:500] for note in notes[:50]]
    vehicle_out = {
        "year": str(vehicle.get("year") or "")[:10],
        "make": str(vehicle.get("make") or "")[:80],
        "model": str(vehicle.get("model") or "")[:80],
        "trim": str(vehicle.get("trim") or "")[:80],
        "body_class": str(vehicle.get("body_class") or "")[:80],
        "body_style": normalize_body_style(vehicle.get("body_style") or vehicle.get("body_class"), vehicle.get("doors")),
        "doors": str(vehicle.get("doors") or "")[:8],
        "drive": str(vehicle.get("drive") or "")[:40],
        "engine": str(vehicle.get("engine") or "")[:120],
    }
    customer_out = {
        "first_name": str(customer.get("first_name") or "")[:80],
        "last_name": str(customer.get("last_name") or "")[:80],
        "phone": str(customer.get("phone") or "")[:40],
        "email": str(customer.get("email") or "")[:120],
        "insurance_company": str(customer.get("insurance_company") or "")[:120],
        "claim_number": str(customer.get("claim_number") or "")[:64],
    }
    return {
        "customer": customer_out,
        "vehicle": vehicle_out,
        "vin": str(data.get("vin") or "")[:32].upper(),
        "lines": summary["lines"],
        "totals": {key: value for key, value in summary.items() if key != "lines"},
        "rates": rates,
        "notes": clean_notes,
    }, None


@router.post("/native-estimates/preview")
async def preview_native_estimate(request: Request):
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        rates = data.get("rates") if isinstance(data.get("rates"), dict) else _load_rates(cur, scope)
        payload, payload_error = _payload_from_body({**data, "lines": data.get("lines") or []}, rates)
        if payload_error:
            return JSONResponse(status_code=400, content={"error": payload_error})
        return {"totals": payload["totals"], "lines": payload["lines"], "rates": rates}
    finally:
        cur.close()


@router.get("/native-estimates")
async def list_native_estimates(request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        cur.execute(
            """
            SELECT public_id, estimate_number, version, supplement_number, status, ro,
                   vin, customer, vehicle, totals, updated_at
            FROM native_estimates
            WHERE deleted_at IS NULL
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
            ORDER BY updated_at DESC
            LIMIT 200
            """,
            (scope["shop_uuid"], scope["shop_id"], scope["domain"]),
        )
        rows = []
        for row in cur.fetchall() or []:
            item = _public_estimate(row)
            rows.append(
                {
                    "id": item["id"],
                    "estimate_number": item["estimate_number"],
                    "version": item["version"],
                    "supplement_number": item["supplement_number"],
                    "status": item["status"],
                    "ro": item["ro"],
                    "vin": item["vin"],
                    "vehicle": " ".join(
                        part
                        for part in (
                            item["vehicle"].get("year"),
                            item["vehicle"].get("make"),
                            item["vehicle"].get("model"),
                        )
                        if part
                    ),
                    "customer": " ".join(
                        part for part in (item["customer"].get("first_name"), item["customer"].get("last_name")) if part
                    ),
                    "total": (item.get("totals") or {}).get("grand_total"),
                }
            )
        return {"estimates": rows}
    finally:
        cur.close()


@router.post("/native-estimates")
async def save_native_estimate(request: Request):
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        rates = _load_rates(cur, scope)
        payload, payload_error = _payload_from_body(data, rates)
        if payload_error:
            return JSONResponse(status_code=400, content={"error": payload_error})
        public_id = str(data.get("id") or "").strip()
        user = scope["user"]
        if public_id:
            existing = _load_estimate(cur, scope, public_id)
            if not existing:
                return JSONResponse(status_code=404, content={"error": "Estimate not found"})
            cur.execute(
                """
                UPDATE native_estimates
                SET customer = %s::jsonb,
                    vehicle = %s::jsonb,
                    vin = %s,
                    lines = %s::jsonb,
                    totals = %s::jsonb,
                    rates = %s::jsonb,
                    notes = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE public_id = %s::uuid
                """,
                (
                    json.dumps(payload["customer"]),
                    json.dumps(payload["vehicle"]),
                    payload["vin"],
                    json.dumps(payload["lines"]),
                    json.dumps(payload["totals"]),
                    json.dumps(payload["rates"]),
                    json.dumps(payload["notes"]),
                    public_id,
                ),
            )
            action = "update"
        else:
            public_id = str(uuid.uuid4())
            cur.execute("SELECT COALESCE(MAX(estimate_number), 701) AS max_number FROM native_estimates WHERE domain = %s", (scope["domain"],))
            next_number = int((cur.fetchone() or {}).get("max_number") or 701) + 1
            cur.execute(
                """
                INSERT INTO native_estimates (
                    public_id, domain, shop_id, shop_uuid, estimate_number, version,
                    supplement_number, status, customer, vehicle, vin, lines, totals, rates, notes, created_by
                )
                VALUES (%s::uuid, %s, %s, %s::uuid, %s, 1, 0, 'draft', %s::jsonb, %s::jsonb, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s)
                """,
                (
                    public_id,
                    scope["domain"],
                    scope["shop_id"],
                    scope["shop_uuid"],
                    next_number,
                    json.dumps(payload["customer"]),
                    json.dumps(payload["vehicle"]),
                    payload["vin"],
                    json.dumps(payload["lines"]),
                    json.dumps(payload["totals"]),
                    json.dumps(payload["rates"]),
                    json.dumps(payload["notes"]),
                    user.get("id"),
                ),
            )
            action = "create"
        saved = _load_estimate(cur, scope, public_id)
        write_audit(
            cur,
            domain=scope["domain"],
            shop_id=scope["shop_id"],
            actor_user_id=user.get("id"),
            actor_email=user.get("email"),
            action=action,
            entity_type="estimate",
            entity_id=public_id,
            after={"total": payload["totals"].get("grand_total"), "vin": payload["vin"]},
        )
        conn.commit()
        return {"status": "ok", "estimate": _public_estimate(saved)}
    finally:
        cur.close()


@router.get("/native-estimates/{public_id}")
async def get_native_estimate(public_id: str, request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        row = _load_estimate(cur, scope, public_id)
        if not row:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})
        return {"estimate": _public_estimate(row)}
    finally:
        cur.close()


@router.post("/native-estimates/{public_id}/supplement")
async def supplement_native_estimate(public_id: str, request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        existing = _load_estimate(cur, scope, public_id)
        if not existing:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})
        new_id = str(uuid.uuid4())
        user = scope["user"]
        cur.execute(
            """
            INSERT INTO native_estimates (
                public_id, domain, shop_id, shop_uuid, estimate_number, version, supplement_number,
                parent_public_id, status, ro, customer, vehicle, vin, lines, totals, rates, notes, created_by
            )
            VALUES (
                %s::uuid, %s, %s, %s::uuid, %s, %s, %s, %s::uuid, 'draft', %s,
                %s::jsonb, %s::jsonb, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s
            )
            """,
            (
                new_id,
                scope["domain"],
                scope["shop_id"],
                scope["shop_uuid"],
                existing.get("estimate_number"),
                int(existing.get("version") or 1) + 1,
                int(existing.get("supplement_number") or 0) + 1,
                public_id,
                existing.get("ro"),
                json.dumps(existing.get("customer") if isinstance(existing.get("customer"), (dict, list)) else json.loads(existing.get("customer") or "{}")),
                json.dumps(existing.get("vehicle") if isinstance(existing.get("vehicle"), (dict, list)) else json.loads(existing.get("vehicle") or "{}")),
                existing.get("vin"),
                json.dumps(existing.get("lines") if isinstance(existing.get("lines"), list) else json.loads(existing.get("lines") or "[]")),
                json.dumps(existing.get("totals") if isinstance(existing.get("totals"), dict) else json.loads(existing.get("totals") or "{}")),
                json.dumps(existing.get("rates") if isinstance(existing.get("rates"), dict) else json.loads(existing.get("rates") or "{}")),
                json.dumps(existing.get("notes") if isinstance(existing.get("notes"), list) else json.loads(existing.get("notes") or "[]")),
                user.get("id"),
            ),
        )
        write_audit(
            cur,
            domain=scope["domain"],
            shop_id=scope["shop_id"],
            actor_user_id=user.get("id"),
            actor_email=user.get("email"),
            action="supplement",
            entity_type="estimate",
            entity_id=new_id,
            after={"parent": public_id},
        )
        conn.commit()
        saved = _load_estimate(cur, scope, new_id)
        return {"status": "ok", "estimate": _public_estimate(saved)}
    finally:
        cur.close()


@router.post("/native-estimates/{public_id}/convert")
async def convert_native_estimate(public_id: str, request: Request):
    data = {}
    try:
        data = await request.json()
    except Exception:
        data = {}
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        row = _load_estimate(cur, scope, public_id)
        if not row:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})
        estimate = _public_estimate(row)
        vehicle = estimate["vehicle"]
        customer = estimate["customer"]
        owner = " ".join(part for part in (customer.get("first_name"), customer.get("last_name")) if part).strip()
        if customer.get("phone"):
            owner = f"{owner}\n{customer['phone']}" if owner else customer["phone"]
        incoming = {
            "ro": estimate.get("ro") or "",
            "vin": estimate.get("vin"),
            "year": vehicle.get("year"),
            "make": vehicle.get("make"),
            "model": vehicle.get("model"),
            "customer": owner,
        }
        matches = query_duplicate_matches(cur, domain=scope["domain"], shop_id=scope["shop_id"], shop_uuid=scope["shop_uuid"], incoming=incoming)
        if matches and not data.get("acknowledge_duplicate"):
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Possible duplicate repair order",
                    "code": "duplicate_warning",
                    "duplicates": matches,
                },
            )
        documents = to_repair_order_documents(estimate["lines"], estimate["rates"], int((estimate["totals"] or {}).get("deductible_cents") or 0))
        ro_value = str(estimate.get("ro") or "").strip() or _allocate_ro(cur, scope["domain"])
        totals = documents["estimate_totals"]
        vehicle_text = " ".join(part for part in (vehicle.get("year"), vehicle.get("make"), vehicle.get("model")) if part)
        cur.execute(
            """
            SELECT id FROM saved_estimates
            WHERE domain = %s AND ro = %s
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (scope["domain"], ro_value),
        )
        existing_ro = cur.fetchone()
        params = (
            vehicle_text,
            vehicle.get("year"),
            vehicle.get("make"),
            vehicle.get("model"),
            owner,
            customer.get("insurance_company"),
            estimate.get("vin"),
            customer.get("claim_number"),
            scope["user"].get("email"),
            scope["user"].get("email"),
            json.dumps(documents["labor_repairs"]),
            json.dumps(documents["paint_repairs"]),
            json.dumps(documents["parts_repairs"]),
            json.dumps({"source": "native-estimate", "estimate_id": public_id, "version": estimate["version"]}),
            json.dumps(totals),
            totals.get("parts_total"),
            totals.get("grand_total"),
            totals.get("deductible"),
            totals.get("customer_pay"),
            totals.get("insurance_pay"),
        )
        if existing_ro:
            cur.execute(
                """
                UPDATE saved_estimates
                SET vehicle = %s, year = %s, make = %s, model = %s, owner_info = %s,
                    insurance_company = %s, vin = %s, claim_number = %s, written_by = %s, estimator = %s,
                    labor_repairs = %s::jsonb, paint_repairs = %s::jsonb, parts_repairs = %s::jsonb,
                    estimate_snapshot = %s::jsonb, estimate_totals = %s::jsonb,
                    parts_total = %s, grand_total = %s, deductible = %s, customer_pay = %s, insurance_pay = %s,
                    source = 'native', saved_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (*params, existing_ro.get("id")),
            )
        else:
            cur.execute(
                """
                INSERT INTO saved_estimates (
                    ro, vehicle, year, make, model, owner_info, insurance_company, vin, claim_number,
                    written_by, estimator, labor_repairs, paint_repairs, parts_repairs, estimate_snapshot,
                    estimate_totals, parts_total, grand_total, deductible, customer_pay, insurance_pay,
                    in_date, domain, shop_id, shop_uuid, source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb,
                        %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid, 'native')
                """,
                (
                    ro_value,
                    *params,
                    date.today(),
                    scope["domain"],
                    scope["shop_id"],
                    scope["shop_uuid"],
                ),
            )
        from app.routes.UI.ui_with_processing import (
            _recalculate_ro_assignment_hours,
            _refresh_role_assignments_from_lines,
            _sync_ro_line_assignments_for_estimate_update,
        )

        inserted = _sync_ro_line_assignments_for_estimate_update(
            cur, scope["domain"], ro_value, documents["labor_repairs"], documents["paint_repairs"]
        )
        _refresh_role_assignments_from_lines(cur, scope["domain"], ro_value, inserted)
        _recalculate_ro_assignment_hours(cur, scope["domain"], ro_value, documents["labor_repairs"], documents["paint_repairs"])
        cur.execute(
            """
            UPDATE native_estimates
            SET status = 'converted', ro = %s, updated_at = CURRENT_TIMESTAMP
            WHERE public_id = %s::uuid
            """,
            (ro_value, public_id),
        )
        write_audit(
            cur,
            domain=scope["domain"],
            shop_id=scope["shop_id"],
            actor_user_id=scope["user"].get("id"),
            actor_email=scope["user"].get("email"),
            action="convert",
            entity_type="repair_order",
            entity_id=ro_value,
            after={"estimate_id": public_id, "grand_total": totals.get("grand_total"), "duplicates_acknowledged": bool(matches)},
        )
        conn.commit()
        return {"status": "ok", "ro": ro_value, "duplicate_warnings": matches}
    finally:
        cur.close()


@router.post("/tech-assignment/quick")
async def quick_assign_tech(request: Request):
    data = await request.json()
    ro_value = str(data.get("ro") or "").strip()
    repair_type = str(data.get("repair_type") or "body").strip().lower()
    if repair_type not in {"body", "paint", "mech", "frame"}:
        return JSONResponse(status_code=400, content={"error": "repair_type must be body, paint, mech, or frame"})
    try:
        tech_id = int(data.get("tech_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "tech_id is required"})
    if not ro_value:
        return JSONResponse(status_code=400, content={"error": "ro is required"})
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        cur.execute(
            """
            SELECT id, first_name, last_name
            FROM techs
            WHERE id = %s
              AND active = TRUE
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
            LIMIT 1
            """,
            (tech_id, scope["shop_uuid"], scope["shop_id"], scope["domain"]),
        )
        tech = cur.fetchone()
        if not tech:
            return JSONResponse(status_code=404, content={"error": "Technician not found"})
        tech_name = " ".join(part for part in (tech.get("first_name"), tech.get("last_name")) if part).strip()
        cur.execute(
            """
            UPDATE ro_line_assignments
            SET tech_id = %s,
                tech_name = %s,
                is_pending = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE ro = %s
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
              AND (repair_type = %s OR source_repair_type = %s)
              AND (
                    tech_name IS NULL
                 OR BTRIM(tech_name) = ''
                 OR LOWER(BTRIM(tech_name)) = 'unassigned'
              )
            """,
            (tech_id, tech_name, ro_value, scope["shop_uuid"], scope["shop_id"], scope["domain"], repair_type, repair_type),
        )
        updated = int(cur.rowcount or 0)
        write_audit(
            cur,
            domain=scope["domain"],
            shop_id=scope["shop_id"],
            actor_user_id=scope["user"].get("id"),
            actor_email=scope["user"].get("email"),
            action="quick_assign",
            entity_type="repair_order",
            entity_id=ro_value,
            after={"tech": tech_name, "repair_type": repair_type, "lines": updated},
        )
        conn.commit()
        return {"status": "ok", "updated": updated, "tech_name": tech_name}
    finally:
        cur.close()


@router.get("/exports/reports.csv")
async def export_reports_csv(request: Request):
    user = get_authenticated_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if not snapshot_can_view_financials(user.get("permissions")):
        return JSONResponse(status_code=403, content={"error": "Financial reports are hidden for this role"})
    from app.services.db import get_closed_ros_and_summary

    rows, summary = get_closed_ros_and_summary(user.get("domain") or "")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["RO", "Vehicle", "Customer", "Insurance", "Hours", "Parts sales", "Parts cost", "Labor sales", "Labor cost", "Total sales", "Total cost"])
    for row in rows:
        writer.writerow(
            [
                row.get("ro_number"),
                row.get("vehicle"),
                row.get("customer"),
                row.get("insurance"),
                row.get("hours"),
                row.get("parts_sales"),
                row.get("parts_cost"),
                row.get("labor_sales"),
                row.get("labor_cost"),
                row.get("total_sales"),
                row.get("total_cost"),
            ]
        )
    writer.writerow([])
    for name, values in summary.items():
        writer.writerow([name, values.get("sales"), values.get("gp_percent"), values.get("gp_dollar")])
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flagtech-reports.csv"},
    )


@router.get("/exports/native-estimates/{public_id}.pdf")
async def export_estimate_pdf(public_id: str, request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        if not snapshot_can_view_financials(scope["user"].get("permissions")):
            return JSONResponse(status_code=403, content={"error": "Financial printouts are hidden for this role"})
        row = _load_estimate(cur, scope, public_id)
        if not row:
            return JSONResponse(status_code=404, content={"error": "Estimate not found"})
        estimate = _public_estimate(row)
        vehicle = estimate["vehicle"]
        customer = estimate["customer"]
        lines = [
            f"Estimate {estimate.get('estimate_number')}  v{estimate.get('version')}  supplement {estimate.get('supplement_number')}",
            f"Customer: {customer.get('first_name', '')} {customer.get('last_name', '')}",
            f"Vehicle: {vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('trim', '')}",
            f"VIN: {estimate.get('vin') or '-'}",
            f"RO: {estimate.get('ro') or 'not converted'}",
            "",
        ]
        for line in estimate["lines"]:
            lines.append(
                f"{line.get('line')} {line.get('operation')} {line.get('part_name')}  "
                f"qty {line.get('quantity')}  ${int(line.get('price_cents') or 0)/100:.2f}  "
                f"body {line.get('body_hours')}  ref {line.get('refinish_hours')}"
            )
        totals = estimate.get("totals") or {}
        lines.append("")
        lines.append(f"Grand total ${totals.get('grand_total', '0.00')}")
        lines.append(f"Insurance ${totals.get('insurance_pay', '0.00')}   Customer ${totals.get('customer_pay', '0.00')}")
        pdf = render_text_pdf("FlagTech estimate", lines)
        return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=estimate-{public_id}.pdf"})
    finally:
        cur.close()


@router.get("/exports/ro/{ro_number}.pdf")
async def export_ro_pdf(ro_number: str, request: Request):
    conn = get_conn()
    cur = conn.cursor()
    try:
        scope, error = _scope_or_response(request, cur)
        if error:
            return error
        if not snapshot_can_view_financials(scope["user"].get("permissions")):
            return JSONResponse(status_code=403, content={"error": "Financial printouts are hidden for this role"})
        cur.execute(
            """
            SELECT ro, vehicle, year, make, model, owner_info, vin, insurance_company,
                   claim_number, grand_total, parts_total, customer_pay, insurance_pay
            FROM saved_estimates
            WHERE ro = %s
              AND (
                    shop_uuid = %s::uuid
                 OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
              )
            ORDER BY saved_at DESC, id DESC
            LIMIT 1
            """,
            (ro_number, scope["shop_uuid"], scope["shop_id"], scope["domain"]),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "Repair order not found"})
        lines = [
            f"RO {row.get('ro')}",
            f"Vehicle: {row.get('vehicle') or ''}",
            f"Customer: {row.get('owner_info') or ''}",
            f"VIN: {row.get('vin') or ''}",
            f"Insurance: {row.get('insurance_company') or ''}  claim {row.get('claim_number') or ''}",
            f"Parts ${row.get('parts_total') or 0}",
            f"Grand ${row.get('grand_total') or 0}",
            f"Insurance pay ${row.get('insurance_pay') or 0}",
            f"Customer pay ${row.get('customer_pay') or 0}",
        ]
        pdf = render_text_pdf("FlagTech repair order", lines)
        return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=ro-{ro_number}.pdf"})
    finally:
        cur.close()
