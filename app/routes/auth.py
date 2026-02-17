from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.auth import (
    SESSION_COOKIE_NAME,
    create_session_for_user,
    delete_session_by_token,
    get_session_by_token,
    get_user_by_email,
    verify_password,
)

router = APIRouter()


def _render_login_page(error: str = "") -> str:
    error_html = f"<div style='color:#b22222; margin-bottom:12px;'>{error}</div>" if error else ""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>FlagTech Login</title>
</head>
<body style="font-family: Arial, sans-serif; background:#d3d3d3; margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;">
    <div style="width:380px; background:#f2f0ef; padding:28px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.15);">
        <h2 style="margin:0 0 16px 0; color:#3c4142;">FlagTech Login</h2>
        {error_html}
        <form method="post" action="/auth/login">
            <label for="email" style="display:block; margin-bottom:6px; font-weight:bold;">Email</label>
            <input id="email" name="email" type="email" required style="width:100%; padding:10px; margin-bottom:14px; border:1px solid #bbb; border-radius:4px;" />

            <label for="password" style="display:block; margin-bottom:6px; font-weight:bold;">Password</label>
            <input id="password" name="password" type="password" required style="width:100%; padding:10px; margin-bottom:18px; border:1px solid #bbb; border-radius:4px;" />

            <button type="submit" style="width:100%; padding:11px; border:none; border-radius:4px; background:#b22222; color:#fff; font-weight:bold; cursor:pointer;">Sign In</button>
        </form>
    </div>
</body>
</html>
"""


@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    session = get_session_by_token(token) if token else None
    if session:
        return RedirectResponse(url="/ui/", status_code=303)
    return HTMLResponse(_render_login_page())


@router.post("/auth/login", response_class=HTMLResponse)
async def login_submit(email: str = Form(...), password: str = Form(...)):
    normalized_email = (email or "").strip().lower()
    user = get_user_by_email(normalized_email)

    if not user or not user.get("active"):
        return HTMLResponse(_render_login_page("Invalid email or password."), status_code=401)

    if not verify_password(password, user.get("password_hash") or ""):
        return HTMLResponse(_render_login_page("Invalid email or password."), status_code=401)

    session_token = create_session_for_user(user)
    response = RedirectResponse(url="/ui/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    response.set_cookie(
        key="user_domain",
        value=user.get("domain") or "",
        httponly=False,
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    return response


@router.get("/auth/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    delete_session_by_token(token)
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie("user_domain", path="/")
    return response
