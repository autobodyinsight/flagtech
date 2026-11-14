"""Password reset and optional MFA.

Existing users keep the current login path. MFA is off until that user turns
it on. Password reset never changes the architect account.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.routes.estimate_modules.auth_utils import _is_architect_email
from app.routes.estimate_routes._shared import hash_password
from app.services.db import get_conn
from app.services.middleware import get_authenticated_user
from app.services.totp import generate_secret, provisioning_uri, verify_code

router = APIRouter()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/auth/forgot-password")
async def forgot_password(request: Request):
    data = await request.json()
    email = str(data.get("email") or "").strip().lower()
    generic = {"status": "ok", "message": "If that account exists, a reset token was created."}
    if not email or _is_architect_email(email):
        return generic
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id FROM shop_users
            WHERE LOWER(email) = %s AND active = TRUE
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (email,),
        )
        row = cur.fetchone() or {}
        user_id = int(row.get("id") or 0)
        if not user_id:
            return generic
        token = secrets.token_urlsafe(32)
        cur.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, _hash_token(token), datetime.now(timezone.utc) + timedelta(hours=2)),
        )
        conn.commit()
        # Email delivery is environment-specific. The token is not logged.
        # Local setups can opt in to returning it for a password-reset test.
        import os

        if os.getenv("FLAGTECH_RETURN_RESET_TOKEN") == "1":
            return {"status": "ok", "reset_token": token}
        return generic
    finally:
        cur.close()


@router.post("/auth/reset-password")
async def reset_password(request: Request):
    data = await request.json()
    token = str(data.get("token") or "").strip()
    password = str(data.get("password") or "")
    if len(password) < 10:
        return JSONResponse(status_code=400, content={"error": "Password must be at least 10 characters"})
    if not token:
        return JSONResponse(status_code=400, content={"error": "token is required"})
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT t.id, t.user_id, su.email
            FROM password_reset_tokens t
            JOIN shop_users su ON su.id = t.user_id
            WHERE t.token_hash = %s
              AND t.used_at IS NULL
              AND t.expires_at > CURRENT_TIMESTAMP
            LIMIT 1
            """,
            (_hash_token(token),),
        )
        row = cur.fetchone() or {}
        if not row:
            return JSONResponse(status_code=400, content={"error": "Reset token is invalid or expired"})
        if _is_architect_email(row.get("email")):
            return JSONResponse(status_code=400, content={"error": "This account cannot be reset here"})
        cur.execute(
            "UPDATE shop_users SET password_hash = %s WHERE id = %s",
            (hash_password(password), int(row.get("user_id") or 0)),
        )
        cur.execute(
            "UPDATE password_reset_tokens SET used_at = CURRENT_TIMESTAMP WHERE id = %s",
            (int(row.get("id") or 0),),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()


@router.post("/auth/mfa/setup")
async def mfa_setup(request: Request):
    user = get_authenticated_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if user.get("is_architect") or _is_architect_email(user.get("email")):
        return JSONResponse(status_code=400, content={"error": "MFA setup is not available for this account"})
    secret = generate_secret()
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO user_mfa (user_id, enabled, totp_secret, updated_at)
            VALUES (%s, FALSE, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) DO UPDATE SET
                totp_secret = EXCLUDED.totp_secret,
                enabled = FALSE,
                updated_at = CURRENT_TIMESTAMP
            """,
            (int(user["id"]), secret),
        )
        conn.commit()
    finally:
        cur.close()
    return {
        "status": "ok",
        "secret": secret,
        "otpauth_uri": provisioning_uri(secret, user.get("email") or ""),
        "enabled": False,
    }


@router.post("/auth/mfa/enable")
async def mfa_enable(request: Request):
    user = get_authenticated_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if user.get("is_architect"):
        return JSONResponse(status_code=400, content={"error": "MFA setup is not available for this account"})
    data = await request.json()
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT totp_secret FROM user_mfa WHERE user_id = %s", (int(user["id"]),))
        row = cur.fetchone() or {}
        secret = str(row.get("totp_secret") or "")
        if not secret or not verify_code(secret, data.get("code")):
            return JSONResponse(status_code=400, content={"error": "Invalid authentication code"})
        cur.execute(
            "UPDATE user_mfa SET enabled = TRUE, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (int(user["id"]),),
        )
        conn.commit()
        return {"status": "ok", "enabled": True}
    finally:
        cur.close()


@router.post("/auth/mfa/disable")
async def mfa_disable(request: Request):
    user = get_authenticated_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    data = await request.json()
    from app.routes.estimate_routes._shared import verify_password

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM shop_users WHERE id = %s", (int(user["id"]),))
        row = cur.fetchone() or {}
        valid, _upgrade = verify_password(str(data.get("password") or ""), row.get("password_hash"))
        if not valid:
            return JSONResponse(status_code=400, content={"error": "Password did not match"})
        cur.execute("UPDATE user_mfa SET enabled = FALSE, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s", (int(user["id"]),))
        conn.commit()
        return {"status": "ok", "enabled": False}
    finally:
        cur.close()
