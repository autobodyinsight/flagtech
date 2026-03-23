from fastapi import Request
from app.services.middleware import get_authenticated_user, get_authenticated_user_email, get_architect_email_setting


def _resolve_request_user_email(request: Request) -> str:
    return get_authenticated_user_email(request)


def _is_architect_email(email: str) -> bool:
    normalized = str(email or "").strip().lower()
    architect_email = get_architect_email_setting()
    return bool(normalized) and bool(architect_email) and normalized == architect_email


def _build_cookie_secure_flag(request: Request) -> bool:
    proto = str(request.headers.get("x-forwarded-proto") or "").strip().lower()
    return proto == "https"


def _resolve_internal_access_level(request: Request) -> str:
    authenticated_user = get_authenticated_user(request) or {}
    request_email = _resolve_request_user_email(request)
    if _is_architect_email(request_email):
        return "ARCHITECT"
    access_level = str(authenticated_user.get("access_level") or "").strip().upper()
    if access_level:
        return access_level
    return "USER"


def _request_is_architect(request: Request) -> bool:
    return _resolve_internal_access_level(request) == "ARCHITECT"


def _resolve_setup_scope_domain(request: Request, fallback_domain: str, requested_domain: str | None) -> str:
    requested = str(requested_domain or "").strip().lower()
    if requested and _request_is_architect(request):
        return requested
    return str(fallback_domain or "").strip().lower()
