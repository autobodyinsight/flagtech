"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse

from fastapi import Request


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the user's domain with authenticated session taking priority."""
    state_user = getattr(request.state, "user", None)
    if isinstance(state_user, dict):
        value = _clean(state_user.get("domain"))
        if value:
            return value

    # Backward-compatible fallback paths (used only when no authenticated user context exists).
    header_keys = ("x-user-domain", "x-domain", "x-tenant", "x-organization")
    for key in header_keys:
        value = _clean(request.headers.get(key))
        if value:
            return value

    value = _clean(request.query_params.get("domain"))
    if value:
        return value

    value = _clean(request.cookies.get("domain")) or _clean(request.cookies.get("user_domain"))
    if value:
        return value

    origin = _clean(request.headers.get("origin")) or _clean(request.headers.get("referer"))
    if origin:
        try:
            host = urlparse(origin).hostname
            value = _clean(host)
            if value:
                return value
        except Exception:
            pass

    host = _clean(request.headers.get("host"))
    if host:
        return host.split(":")[0]

    return None
