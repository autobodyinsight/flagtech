#!/usr/bin/env python3
"""One-time admin script to reset Jorge's login password securely."""

import os
import sys
from getpass import getpass

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.auth import ARCHITECT_EMAIL, hash_password
from app.services.db import get_conn


def _prompt_password() -> str:
    password = getpass("Enter new password for jorge@autobodyinsight.com: ")
    confirm = getpass("Confirm new password: ")
    if password != confirm:
        raise ValueError("Passwords do not match")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return password


def main() -> int:
    if ARCHITECT_EMAIL != "jorge@autobodyinsight.com":
        print("Configured architect email is invalid.")
        return 1

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL is not set.")
        return 1

    try:
        password = _prompt_password()
    except ValueError as exc:
        print(str(exc))
        return 1

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM users
        WHERE lower(email) = lower(%s)
        LIMIT 1
        """,
        (ARCHITECT_EMAIL,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        print("Jorge account not found. Create jorge@autobodyinsight.com first, then rerun this script.")
        return 1

    new_hash = hash_password(password)

    cur.execute(
        """
        UPDATE users
        SET password_hash = %s,
            active = TRUE,
            access_level = 'architect'
        WHERE lower(email) = lower(%s)
        RETURNING id, email
        """,
        (new_hash, ARCHITECT_EMAIL),
    )
    updated = cur.fetchone()

    cur.execute(
        """
        UPDATE users
        SET access_level = 'manager'
        WHERE lower(access_level) = 'architect' AND lower(email) <> lower(%s)
        """,
        (ARCHITECT_EMAIL,),
    )

    cur.close()

    if not updated:
        print("No account updated.")
        return 1

    print("Password reset complete for jorge@autobodyinsight.com.")
    print("This is a one-time admin utility; delete scripts/reset_jorge_password.py after use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
