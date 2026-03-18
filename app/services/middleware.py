"""Request helpers without authentication logic."""

from __future__ import annotations

from typing import Optional

from fastapi import Request


DEFAULT_SCOPE_DOMAIN = "default"


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _build_scope_key(domain: str | None) -> str:
    normalized = str(domain or "").strip().lower()
    return normalized or DEFAULT_SCOPE_DOMAIN


def get_user_domain(request: Request) -> Optional[str]:
    query_domain = _clean(request.query_params.get("scope"))
    header_domain = _clean(request.headers.get("x-scope"))
    return _build_scope_key(query_domain or header_domain or DEFAULT_SCOPE_DOMAIN)
