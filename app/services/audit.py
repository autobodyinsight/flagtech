"""Append-only audit rows for estimates, repair orders, and payments."""

from __future__ import annotations

import json


def write_audit(
    cur,
    *,
    domain: str | None,
    shop_id: int | None,
    actor_user_id: int | None,
    actor_email: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None,
    before=None,
    after=None,
) -> None:
    cur.execute(
        """
        INSERT INTO audit_log (
            domain, shop_id, actor_user_id, actor_email, action,
            entity_type, entity_id, before_data, after_data
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            str(domain or "").strip().lower() or None,
            int(shop_id) if shop_id else None,
            int(actor_user_id) if actor_user_id else None,
            str(actor_email or "").strip().lower() or None,
            str(action or "")[:64],
            str(entity_type or "")[:64],
            str(entity_id or "")[:128] or None,
            json.dumps(before) if before is not None else None,
            json.dumps(after) if after is not None else None,
        ),
    )
