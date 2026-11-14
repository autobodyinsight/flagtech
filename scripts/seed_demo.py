"""Demo shop data for an empty database.

This script never updates or deletes shop_users. If the Autobody Insight shop
already has repair orders, it leaves them alone.
"""

from __future__ import annotations

import os
import uuid

from app.services.db import get_conn
from app.services.schema_bootstrap import initialize_application_schema


DEMO_DOMAIN = "autobodyinsight.com"
DEMO_ORG = "Autobody Insight"


def main() -> None:
    initialize_application_schema()
    conn = get_conn()
    cur = conn.cursor()
    try:
        user_count = _count(cur, "SELECT COUNT(*) AS n FROM shop_users")
        cur.execute("SELECT id, shop_id FROM shops WHERE domain = %s", (DEMO_DOMAIN,))
        shop = cur.fetchone()
        if not shop:
            org_uuid = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO organizations (organization_id, name) VALUES (%s::uuid, %s) RETURNING id",
                (org_uuid, DEMO_ORG),
            )
            org_id = int((cur.fetchone() or {}).get("id"))
            shop_uuid = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO shops (shop_id, domain, name, active, organization_id)
                VALUES (%s::uuid, %s, %s, TRUE, %s)
                RETURNING id, shop_id
                """,
                (shop_uuid, DEMO_DOMAIN, DEMO_ORG, org_id),
            )
            shop = cur.fetchone()
            print(f"created shop {DEMO_DOMAIN}")
        else:
            print(f"shop {DEMO_DOMAIN} already exists")

        shop_id = int(shop.get("id"))
        shop_uuid = str(shop.get("shop_id"))
        estimates = _count(cur, "SELECT COUNT(*) AS n FROM saved_estimates WHERE domain = %s", (DEMO_DOMAIN,))
        if estimates == 0:
            cur.execute(
                """
                INSERT INTO saved_estimates (
                    ro, vehicle, year, make, model, owner_info, insurance_company, vin,
                    labor_repairs, paint_repairs, parts_repairs, estimate_totals,
                    parts_total, grand_total, deductible, customer_pay, insurance_pay,
                    domain, shop_id, shop_uuid, source
                )
                VALUES (
                    'DEMO1001', '2020 Honda Civic', '2020', 'Honda', 'Civic',
                    E'Case Sample\n555-0100', 'Sample Mutual', '1HGCM82633A004352',
                    '[{"line":"1","description":"Repair door","value":"2.0"}]'::jsonb,
                    '[{"line":"1","description":"Refinish door","value":"1.5"}]'::jsonb,
                    '[{"line":1,"description":"Door shell","part_type":"OEM","qty":"1","price":"100.00"}]'::jsonb,
                    '{"parts_total":"100.00","grand_total":"250.00","deductible":"50.00","customer_pay":"50.00","insurance_pay":"200.00","body_labor":"100.00","paint_labor":"50.00","frame_labor":"0.00","mechanical_labor":"0.00","glass_labor":"0.00"}'::jsonb,
                    100, 250, 50, 50, 200,
                    %s, %s, %s::uuid, 'demo'
                )
                """,
                (DEMO_DOMAIN, shop_id, shop_uuid),
            )
            cur.execute(
                """
                INSERT INTO ro_line_assignments (
                    ro, repair_type, source_repair_type, line_key, line_number, description, hours, domain, shop_id, shop_uuid
                )
                VALUES
                    ('DEMO1001', 'body', 'body', '1', '1', 'Repair door', 2.0, %s, %s, %s::uuid),
                    ('DEMO1001', 'paint', 'paint', '1', '1', 'Refinish door', 1.5, %s, %s, %s::uuid)
                """,
                (DEMO_DOMAIN, shop_id, shop_uuid, DEMO_DOMAIN, shop_id, shop_uuid),
            )
            print("inserted demo repair order DEMO1001")
        else:
            print("existing repair orders left unchanged")

        techs = _count(cur, "SELECT COUNT(*) AS n FROM techs WHERE domain = %s", (DEMO_DOMAIN,))
        if techs == 0:
            cur.execute(
                """
                INSERT INTO techs (first_name, last_name, pay_rate, domain, active, status, role, shop_id, shop_uuid)
                VALUES ('Alex', 'Rivera', 25, %s, TRUE, 'Active', 'Body', %s, %s::uuid)
                """,
                (DEMO_DOMAIN, shop_id, shop_uuid),
            )
            print("inserted demo technician Alex Rivera")

        cur.execute(
            """
            INSERT INTO shop_labor_rates (
                domain, shop_id, shop_uuid, body_rate_cents, refinish_rate_cents,
                mechanical_rate_cents, frame_rate_cents, paint_materials_per_hour_cents
            )
            VALUES (%s, %s, %s::uuid, 5800, 5800, 7500, 8000, 3600)
            ON CONFLICT (domain) DO NOTHING
            """,
            (DEMO_DOMAIN, shop_id, shop_uuid),
        )
        after_users = _count(cur, "SELECT COUNT(*) AS n FROM shop_users")
        if after_users != user_count:
            raise SystemExit("seed changed shop_users; aborting")
        conn.commit()
        print(f"shop_users unchanged ({user_count})")
    finally:
        cur.close()


def _count(cur, sql, params=None):
    cur.execute(sql, params or ())
    return int((cur.fetchone() or {}).get("n") or 0)


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required")
    main()
