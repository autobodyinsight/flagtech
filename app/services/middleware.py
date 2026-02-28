"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

from typing import Optional

from fastapi import Request


DEFAULT_SCOPE_DOMAIN = "autobodyinsight.com"


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


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the active tenant domain scope for anonymous access."""
    return _build_scope_key(DEFAULT_SCOPE_DOMAIN)
