"""Request helpers for tenant/domain resolution."""

from __future__ import annotations

from typing import Optional

from fastapi import Request

from app.services.auth import build_shop_scope_key


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def get_user_domain(request: Request) -> Optional[str]:
    """Resolve the authenticated user's strict tenant scope key."""
    state_user = getattr(request.state, "user", None)
    if isinstance(state_user, dict):
        value = _clean(state_user.get("domain"))
        if value:
            return build_shop_scope_key(value, state_user.get("company_name"), state_user.get("email"))

        fallback_scope = build_shop_scope_key(None, state_user.get("company_name"), state_user.get("email"))
        value = _clean(fallback_scope)
        if value:
            return value

    return None
