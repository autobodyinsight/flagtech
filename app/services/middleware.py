"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

from typing import Optional

from fastapi import Request
from app.services.db import get_conn


DEFAULT_SCOPE_DOMAIN = "autobodyinsight.com"
ARCHITECT_EMAIL = "jorge@autobodyinsight.com"


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


def _resolve_request_user_email(request: Request) -> str:
    candidates = (
        request.headers.get("x-user-email"),
        request.headers.get("x-auth-request-email"),
        request.headers.get("x-ms-client-principal-name"),
        request.headers.get("remote-user"),
        request.query_params.get("user_email"),
        request.cookies.get("user_email"),
    )
    for value in candidates:
        email = _clean(str(value or "").lower())
        if email:
            return email
    return ""


def _parse_positive_int(value: str | None) -> int | None:
    try:
        parsed = int(str(value or "").strip())
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _resolve_domain_from_shop_id(shop_id: int | None) -> Optional[str]:
    if not shop_id:
        return None
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT domain FROM shops WHERE id = %s LIMIT 1", (shop_id,))
        shop_row = cur.fetchone() or {}
        shop_domain = _normalize_domain(shop_row.get("domain"))
        if shop_domain:
            return shop_domain

        cur.execute("SELECT domain FROM shop_settings WHERE shop_id = %s LIMIT 1", (shop_id,))
        settings_row = cur.fetchone() or {}
        settings_domain = _normalize_domain(settings_row.get("domain"))
        return settings_domain or None
    finally:
        cur.close()


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the active tenant domain scope for authenticated requests."""
    cookie_domain = _clean(request.cookies.get("user_domain"))
    header_domain = _clean(request.headers.get("x-user-domain"))
    query_domain = _clean(request.query_params.get("shop_domain"))
    requester_email = _resolve_request_user_email(request)
    requester_is_architect = requester_email == ARCHITECT_EMAIL
    cookie_shop_id = _parse_positive_int(request.cookies.get("user_shop_id"))
    query_shop_id = _parse_positive_int(request.query_params.get("shop_id"))
    header_shop_id = _parse_positive_int(request.headers.get("x-shop-id"))

    selected_shop_id = None
    if requester_is_architect:
        selected_shop_id = query_shop_id or header_shop_id or cookie_shop_id
    else:
        selected_shop_id = cookie_shop_id

    resolved_domain = _resolve_domain_from_shop_id(selected_shop_id)
    if resolved_domain:
        return _build_scope_key(resolved_domain)

    if requester_is_architect:
        candidate_domain = query_domain or header_domain or cookie_domain
    else:
        # Cookie-scoped tenant wins over caller-provided headers to prevent cross-tenant spoofing.
        candidate_domain = cookie_domain or header_domain
    if not candidate_domain:
        return None

    return _build_scope_key(candidate_domain)
