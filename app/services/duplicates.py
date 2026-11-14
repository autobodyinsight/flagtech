"""Duplicate repair-order detection.

Matches are warnings. Nothing is deleted. Callers decide whether the user
has acknowledged the warning before writing another RO.
"""

from __future__ import annotations

import re


def name_key(value: str | None) -> str:
    tokens = re.findall(r"[a-z0-9]+", str(value or "").lower())
    return " ".join(sorted(tokens))


def normalize_vin(value: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def duplicate_reason(existing: dict, incoming: dict) -> str | None:
    existing_ro = str(existing.get("ro") or "").strip()
    incoming_ro = str(incoming.get("ro") or "").strip()
    if existing_ro and incoming_ro and existing_ro == incoming_ro:
        return None

    existing_vin = normalize_vin(existing.get("vin"))
    incoming_vin = normalize_vin(incoming.get("vin"))
    if len(existing_vin) == 17 and existing_vin == incoming_vin:
        return "same VIN"

    same_vehicle = (
        str(existing.get("year") or "").strip()
        and str(existing.get("year") or "").strip() == str(incoming.get("year") or "").strip()
        and str(existing.get("make") or "").strip().lower() == str(incoming.get("make") or "").strip().lower()
        and str(existing.get("model") or "").strip().lower() == str(incoming.get("model") or "").strip().lower()
    )
    existing_name = name_key(existing.get("customer") or existing.get("owner_info"))
    incoming_name = name_key(incoming.get("customer") or incoming.get("owner_info"))
    if same_vehicle and existing_name and existing_name == incoming_name:
        return "same customer and vehicle"
    return None


def query_duplicate_matches(cur, *, domain: str, shop_id, shop_uuid, incoming: dict) -> list[dict]:
    vin = normalize_vin(incoming.get("vin"))
    year = str(incoming.get("year") or "").strip()
    make = str(incoming.get("make") or "").strip()
    model = str(incoming.get("model") or "").strip()
    if len(vin) != 17 and not (year and make and model):
        return []
    cur.execute(
        """
        SELECT ro, vin, year, make, model, owner_info AS customer, vehicle
        FROM saved_estimates
        WHERE (
                shop_uuid = %s::uuid
             OR (shop_uuid IS NULL AND shop_id = %s AND domain = %s)
        )
          AND (
                (%s <> '' AND UPPER(regexp_replace(COALESCE(vin, ''), '[^A-Za-z0-9]', '', 'g')) = %s)
             OR (%s <> '' AND year = %s AND LOWER(COALESCE(make, '')) = LOWER(%s) AND LOWER(COALESCE(model, '')) = LOWER(%s))
          )
        ORDER BY saved_at DESC
        LIMIT 25
        """,
        (shop_uuid, shop_id, domain, vin, vin, year, year, make, model),
    )
    return find_duplicates(cur.fetchall() or [], incoming)


def find_duplicates(existing_rows: list[dict], incoming: dict) -> list[dict]:
    matches = []
    for row in existing_rows or []:
        reason = duplicate_reason(row, incoming)
        if not reason:
            continue
        matches.append(
            {
                "ro": str(row.get("ro") or ""),
                "vehicle": " ".join(
                    part for part in (str(row.get("year") or ""), str(row.get("make") or ""), str(row.get("model") or "")) if part
                ).strip()
                or str(row.get("vehicle") or ""),
                "customer": str(row.get("customer") or row.get("owner_info") or ""),
                "vin": normalize_vin(row.get("vin")),
                "reason": reason,
            }
        )
    return matches
