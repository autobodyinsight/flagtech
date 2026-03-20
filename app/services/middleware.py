"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Request

from app.services.db import get_conn


DEFAULT_SCOPE_DOMAIN = "autobodyinsight.com"
ARCHITECT_EMAIL = "jorge@autobodyinsight.com"
SESSION_COOKIE_NAME = "session_id"
SESSION_DURATION_HOURS = 12


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _normalize_domain(value: str | None) -> str:
    return (value or "").strip().lower()


def _build_scope_key(domain: str | None) -> str:
    normalized_domain = _normalize_domain(domain)
    if normalized_domain:
        return normalized_domain
    return "default"


def _ensure_auth_sessions_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            session_id VARCHAR(128) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions(expires_at)")


def create_auth_session(user_id: int, duration_hours: int = SESSION_DURATION_HOURS) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=max(1, int(duration_hours or 1)))
    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_auth_sessions_table(cur)
        cur.execute(
            """
            INSERT INTO auth_sessions (session_id, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (token, int(user_id), expires_at),
        )
        conn.commit()
    finally:
        cur.close()
    return token


def revoke_auth_session(session_id: str | None) -> None:
    token = str(session_id or "").strip()
    if not token:
        return

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_auth_sessions_table(cur)
        cur.execute("DELETE FROM auth_sessions WHERE session_id = %s", (token,))
        conn.commit()
    finally:
        cur.close()


def get_authenticated_user(request: Request) -> dict | None:
    session_id = _clean(request.cookies.get(SESSION_COOKIE_NAME))
    if not session_id:
        return None

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_auth_sessions_table(cur)
        cur.execute(
            """
            SELECT
                su.id,
                su.email,
                su.role,
                su.domain,
                su.shop_id,
                COALESCE(ss.shop_name, sh.name, '') AS shop_name,
                COALESCE(ss.address, sh.address, '') AS address,
                s.expires_at
            FROM auth_sessions s
            JOIN shop_users su
              ON su.id = s.user_id
             AND su.active = TRUE
            LEFT JOIN shops sh
              ON sh.id = su.shop_id
            LEFT JOIN shop_settings ss
              ON ss.shop_id = su.shop_id
             AND ss.domain = su.domain
            WHERE s.session_id = %s
              AND s.expires_at > CURRENT_TIMESTAMP
            ORDER BY ss.updated_at DESC NULLS LAST, ss.id DESC
            LIMIT 1
            """,
            (session_id,),
        )
        row = cur.fetchone() or {}
        if not row:
            return None

        return {
            "id": int(row.get("id") or 0),
            "email": str(row.get("email") or "").strip().lower(),
            "role": str(row.get("role") or "").strip(),
            "domain": _build_scope_key(str(row.get("domain") or "").strip().lower()),
            "shop_id": int(row.get("shop_id") or 0) or None,
            "shop_name": str(row.get("shop_name") or "").strip(),
            "address": str(row.get("address") or "").strip(),
            "is_architect": str(row.get("email") or "").strip().lower() == ARCHITECT_EMAIL,
        }
    finally:
        cur.close()


def get_authenticated_user_email(request: Request) -> str:
    user = get_authenticated_user(request)
    if not user:
        return ""
    return str(user.get("email") or "").strip().lower()


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the active tenant domain scope for authenticated requests."""
    user = get_authenticated_user(request)
    if not user:
        return None
    candidate_domain = _clean(str(user.get("domain") or "").lower())
    if not candidate_domain:
        return None
    return _build_scope_key(candidate_domain)
