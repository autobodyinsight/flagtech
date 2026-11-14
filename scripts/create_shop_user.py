"""Insert one shop user with the same columns Setup uses.

Refuses to update an existing email, and refuses the architect email.
The password is read from the FLAGTECH_NEW_USER_PASSWORD environment variable
and is never printed.
"""

from __future__ import annotations

import os
import sys
import uuid

from app.routes.estimate_modules.auth_utils import _is_architect_email
from app.routes.estimate_routes._shared import hash_password
from app.services.db import get_conn
from app.services.schema_bootstrap import initialize_application_schema


ALLOWED = {"Manager", "Estimator", "Tech", "Technician", "Receptionist", "HR", "Support", "Owner", "Admin", "Accounting", "Front Office"}


def main() -> None:
    email = str(os.getenv("FLAGTECH_NEW_USER_EMAIL") or "").strip().lower()
    password = str(os.getenv("FLAGTECH_NEW_USER_PASSWORD") or "")
    role = str(os.getenv("FLAGTECH_NEW_USER_ROLE") or "Manager").strip()
    domain = str(os.getenv("FLAGTECH_NEW_USER_DOMAIN") or "autobodyinsight.com").strip().lower()
    first_name = str(os.getenv("FLAGTECH_NEW_USER_FIRST") or "Alfred").strip()
    last_name = str(os.getenv("FLAGTECH_NEW_USER_LAST") or "Test").strip()
    if not email or len(password) < 12:
        raise SystemExit("FLAGTECH_NEW_USER_EMAIL and a 12+ character FLAGTECH_NEW_USER_PASSWORD are required")
    if role not in ALLOWED:
        raise SystemExit("role is not allowed")
    if _is_architect_email(email):
        raise SystemExit("architect email is off limits")

    initialize_application_schema()
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM shop_users WHERE LOWER(email) = %s LIMIT 1", (email,))
        if cur.fetchone():
            raise SystemExit("user already exists; no changes made")
        cur.execute("SELECT id, shop_id FROM shops WHERE domain = %s LIMIT 1", (domain,))
        shop = cur.fetchone() or {}
        shop_id = int(shop.get("id") or 0)
        shop_uuid = str(shop.get("shop_id") or "")
        if not shop_id or not shop_uuid:
            raise SystemExit("shop domain was not found")
        cur.execute(
            """
            INSERT INTO shop_users (user_id, first_name, last_name, email, role, password_hash, domain, shop_id, shop_uuid, active)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::uuid, TRUE)
            RETURNING id
            """,
            (str(uuid.uuid4()), first_name, last_name, email, role, hash_password(password), domain, shop_id, shop_uuid),
        )
        created = cur.fetchone() or {}
        conn.commit()
        print(f"created user id {created.get('id')} email {email} role {role} domain {domain}")
    finally:
        cur.close()


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required")
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"create user failed: {exc}", file=sys.stderr)
        raise
