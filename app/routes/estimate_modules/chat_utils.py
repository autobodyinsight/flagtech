from fastapi import Request
from app.services.middleware import get_user_domain

from .auth_utils import _resolve_request_user_email
from .db_schema import _ensure_shop_users_table
from .shop_scope import _resolve_request_shop_uuid


def _resolve_current_user_row(request: Request, cur, domain: str) -> dict | None:
    email = _resolve_request_user_email(request)
    normalized_email = str(email or "").strip().lower()
    if not normalized_email:
        return None

    current_shop_uuid = _resolve_request_shop_uuid(request, cur, domain)
    normalized_domain = str(domain or "").strip().lower()
    if not current_shop_uuid and not normalized_domain:
        return None

    _ensure_shop_users_table(cur)
    if current_shop_uuid:
        cur.execute(
            """
                SELECT id, user_id, first_name, last_name, email, role, shop_id, shop_uuid
            FROM shop_users
            WHERE shop_uuid = %s::uuid
              AND LOWER(email) = %s
              AND active = TRUE
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (current_shop_uuid, normalized_email),
        )
    else:
        cur.execute(
            """
                SELECT id, user_id, first_name, last_name, email, role, shop_id, shop_uuid
            FROM shop_users
            WHERE domain = %s
              AND LOWER(email) = %s
              AND active = TRUE
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (normalized_domain, normalized_email),
        )
    return cur.fetchone() or None
