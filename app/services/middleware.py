"""Middleware helpers for authentication and domain filtering."""
from typing import Optional
from fastapi import Request
from app.services.auth import get_session


def _get_request_token(request: Request) -> Optional[str]:
    """Extract an auth token from cookies or Authorization header."""
    token = request.cookies.get("session_token")
    if token:
        return token

    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip() or None

    return request.headers.get("X-Auth-Token")


def get_user_domain(request: Request) -> Optional[str]:
    """Get the current user's domain from the session."""
    token = _get_request_token(request)
    if not token:
        return None
    
    session_data = get_session(token)
    if not session_data:
        return None
    
    return session_data.get("domain")


def get_user_session(request: Request) -> Optional[dict]:
    """Get the current user's full session data."""
    token = _get_request_token(request)
    if not token:
        return None
    
    return get_session(token)
