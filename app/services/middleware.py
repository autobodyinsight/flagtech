"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Request

from app.services.db import get_conn
from app.services.permissions import build_permission_snapshot


DEFAULT_SCOPE_DOMAIN = "autobodyinsight.com"
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
            user_uuid UUID,
            shop_uuid UUID,
            permission_snapshot JSONB,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE auth_sessions ADD COLUMN IF NOT EXISTS user_uuid UUID")
    cur.execute("ALTER TABLE auth_sessions ADD COLUMN IF NOT EXISTS shop_uuid UUID")
    cur.execute("ALTER TABLE auth_sessions ADD COLUMN IF NOT EXISTS permission_snapshot JSONB")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_uuid ON auth_sessions(user_uuid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_shop_uuid ON auth_sessions(shop_uuid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions(expires_at)")


def _ensure_system_settings_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            key VARCHAR(120) PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_system_settings_updated_at ON system_settings(updated_at)")


def get_architect_email_setting() -> str:
    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_system_settings_table(cur)
        cur.execute("SELECT value FROM system_settings WHERE key = %s LIMIT 1", ("architect_email",))
        row = cur.fetchone() or {}
        return str(row.get("value") or "").strip().lower()
    finally:
        cur.close()


def _normalize_permission_snapshot(raw_snapshot) -> dict | None:
    if isinstance(raw_snapshot, dict):
        return raw_snapshot
    if isinstance(raw_snapshot, str):
        try:
            parsed = json.loads(raw_snapshot)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def build_session_snapshot_payload(
    *,
    user: dict,
    permission_snapshot: dict | None = None,
) -> dict:
    normalized_user = user or {}
    resolved_permissions = permission_snapshot or _normalize_permission_snapshot(normalized_user.get("permissions")) or {}
    allowed_features = [
        feature
        for feature, enabled in (resolved_permissions.get("features") or {}).items()
        if bool(enabled)
    ]

    role_value = str(normalized_user.get("role") or "").strip()
    access_level = str(normalized_user.get("access_level") or resolved_permissions.get("access_level") or "").strip()
    shop_domain = str(
        normalized_user.get("domain")
        or resolved_permissions.get("shop_domain")
        or ""
    ).strip().lower()
    shop_id = int(
        normalized_user.get("shop_id")
        or resolved_permissions.get("shop_id")
        or 0
    ) or None
    shop_uuid = str(
        normalized_user.get("shop_uuid")
        or resolved_permissions.get("shop_uuid")
        or ""
    ).strip() or None

    return {
        "user": {
            "id": int(normalized_user.get("id") or 0),
            "user_uuid": str(normalized_user.get("user_uuid") or "").strip() or None,
            "email": str(normalized_user.get("email") or "").strip().lower(),
            "first_name": str(normalized_user.get("first_name") or "").strip(),
            "last_name": str(normalized_user.get("last_name") or "").strip(),
        },
        "role": {
            "name": role_value,
            "access_level": access_level,
            "is_architect": bool(normalized_user.get("is_architect")),
        },
        "shop": {
            "domain": shop_domain,
            "shop_id": shop_id,
            "shop_uuid": shop_uuid,
            "shop_name": str(normalized_user.get("shop_name") or "").strip(),
            "address": str(normalized_user.get("address") or "").strip(),
        },
        "permissions": resolved_permissions,
        "allowed_features": allowed_features,
        "isolation_rules": {
            "enforce_shop_scope": bool(shop_id and shop_uuid and shop_domain),
            "shop_domain": shop_domain,
            "shop_id": shop_id,
            "shop_uuid": shop_uuid,
            "fallback_mode": "deny_if_scope_missing",
        },
    }


def create_auth_session(
    user_id: int,
    permission_snapshot: dict | None = None,
    duration_hours: int = SESSION_DURATION_HOURS,
) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=max(1, int(duration_hours or 1)))
    snapshot_payload = json.dumps(permission_snapshot or {})
    user_uuid = str((permission_snapshot or {}).get("user_uuid") or "").strip() or None
    shop_uuid = str((permission_snapshot or {}).get("shop_uuid") or "").strip() or None
    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_auth_sessions_table(cur)
        cur.execute(
            """
            INSERT INTO auth_sessions (session_id, user_id, user_uuid, shop_uuid, permission_snapshot, expires_at)
            VALUES (%s, %s, %s::uuid, %s::uuid, %s::jsonb, %s)
            """,
            (token, int(user_id), user_uuid, shop_uuid, snapshot_payload, expires_at),
        )
        conn.commit()
    finally:
        cur.close()
    return token


def validate_request_session(request: Request) -> dict | None:
    session_id = _clean(request.cookies.get(SESSION_COOKIE_NAME))
    if not session_id:
        return None

    conn = get_conn()
    cur = conn.cursor()
    try:
        _ensure_auth_sessions_table(cur)
        cur.execute(
            """
            SELECT user_id, permission_snapshot, expires_at
            FROM auth_sessions
            WHERE session_id = %s
              AND expires_at > CURRENT_TIMESTAMP
            LIMIT 1
            """,
            (session_id,),
        )
        row = cur.fetchone() or {}
        if not row:
            return None

        return {
            "user_id": int(row.get("user_id") or 0) or None,
            "permission_snapshot": _normalize_permission_snapshot(row.get("permission_snapshot")) or {},
        }
    finally:
        cur.close()


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
    cached_user = getattr(request.state, "authenticated_user", None)
    if cached_user:
        return cached_user

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
                su.user_id,
                su.first_name,
                su.last_name,
                su.email,
                su.role,
                su.domain,
                su.shop_id,
                su.shop_uuid,
                COALESCE(ss.shop_name, sh.name, '') AS shop_name,
                COALESCE(ss.address, sh.address, '') AS address,
                s.permission_snapshot,
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

        architect_email = get_architect_email_setting()
        normalized_email = str(row.get("email") or "").strip().lower()
        is_architect = bool(architect_email) and normalized_email == architect_email
        normalized_domain = _build_scope_key(str(row.get("domain") or "").strip().lower())
        normalized_shop_id = int(row.get("shop_id") or 0) or None
        normalized_shop_uuid = str(row.get("shop_uuid") or "").strip() or None
        normalized_user_uuid = str(row.get("user_id") or "").strip() or None
        permission_snapshot = _normalize_permission_snapshot(row.get("permission_snapshot"))
        if not permission_snapshot:
            permission_snapshot = build_permission_snapshot(
                role=str(row.get("role") or "").strip(),
                domain=normalized_domain,
                shop_id=normalized_shop_id,
                shop_uuid=normalized_shop_uuid,
                user_uuid=normalized_user_uuid,
                is_architect=is_architect,
            )

        user_payload = {
            "id": int(row.get("id") or 0),
            "first_name": str(row.get("first_name") or "").strip(),
            "last_name": str(row.get("last_name") or "").strip(),
            "email": str(row.get("email") or "").strip().lower(),
            "role": str(row.get("role") or "").strip(),
            "access_level": str(permission_snapshot.get("access_level") or "").strip(),
            "domain": normalized_domain,
            "shop_id": normalized_shop_id,
            "shop_uuid": normalized_shop_uuid,
            "user_uuid": normalized_user_uuid,
            "shop_name": str(row.get("shop_name") or "").strip(),
            "address": str(row.get("address") or "").strip(),
            "is_architect": is_architect,
            "permissions": permission_snapshot,
        }
        request.state.authenticated_user = user_payload
        request.state.session_snapshot = build_session_snapshot_payload(
            user=user_payload,
            permission_snapshot=permission_snapshot,
        )
        request.state.user_id = int(user_payload.get("id") or 0) or None
        return user_payload
    finally:
        cur.close()


def get_authenticated_user_email(request: Request) -> str:
    user = get_authenticated_user(request)
    if not user:
        return ""
    return str(user.get("email") or "").strip().lower()


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the active tenant domain scope for authenticated requests."""
    session_snapshot = getattr(request.state, "session_snapshot", None) or {}
    isolation_rules = session_snapshot.get("isolation_rules") or {}
    scoped_domain = _clean(str(isolation_rules.get("shop_domain") or "").lower())
    if scoped_domain:
        return _build_scope_key(scoped_domain)

    permission_snapshot = getattr(request.state, "permission_snapshot", None) or {}
    snapshot_domain = _clean(str(permission_snapshot.get("shop_domain") or "").lower())
    if snapshot_domain:
        return _build_scope_key(snapshot_domain)

    user = get_authenticated_user(request)
    if not user:
        return None
    candidate_domain = _clean(str(user.get("domain") or "").lower())
    if not candidate_domain:
        return None
    return _build_scope_key(candidate_domain)


def get_user_shop_uuid(request: Request) -> Optional[str]:
    session_snapshot = getattr(request.state, "session_snapshot", None) or {}
    isolation_rules = session_snapshot.get("isolation_rules") or {}
    value = _clean(str(isolation_rules.get("shop_uuid") or ""))
    if value:
        return value

    permission_snapshot = getattr(request.state, "permission_snapshot", None) or {}
    permission_uuid = _clean(str(permission_snapshot.get("shop_uuid") or ""))
    if permission_uuid:
        return permission_uuid

    user = get_authenticated_user(request)
    if not user:
        return None
    user_value = _clean(str(user.get("shop_uuid") or ""))
    return user_value or None
