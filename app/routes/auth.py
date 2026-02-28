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


def _render_login_page(error: str = "", info: str = "") -> str:
    error_html = f"<div class='error-banner'>{error}</div>" if error else ""
    info_html = f"<div class='info-banner'>{info}</div>" if info else ""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>FlagTech Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        :root {{
            --brand-red: #b22222;
            --brand-red-dark: #8f1b1b;
            --brand-gray: #3c4142;
            --brand-gray-soft: #6b7071;
            --surface: #ffffff;
            --surface-soft: #f4f5f6;
            --text: #1f2324;
            --text-muted: #666d6e;
            --border: #d6d9db;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            min-height: 100vh;
            font-family: "Segoe UI", Arial, sans-serif;
            background: linear-gradient(145deg, #2f3334 0%, #3c4142 42%, #b22222 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            color: var(--text);
        }}

        .login-shell {{
            width: 100%;
            max-width: 430px;
            background: var(--surface);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.35);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
            overflow: hidden;
        }}

        .login-header {{
            padding: 18px 22px;
            background: var(--brand-gray);
            border-bottom: 4px solid var(--brand-red);
        }}

        .login-title {{
            margin: 0;
            color: #fff;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}

        .login-subtitle {{
            margin: 6px 0 0;
            color: #d6dadd;
            font-size: 13px;
        }}

        .login-body {{
            padding: 22px;
            background: var(--surface-soft);
        }}

        .error-banner {{
            margin-bottom: 14px;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #e5b4b4;
            background: #fdecec;
            color: var(--brand-red-dark);
            font-size: 13px;
            font-weight: 600;
        }}

        .info-banner {{
            margin-bottom: 14px;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #c8d0d4;
            background: #eef2f4;
            color: #2f3b3f;
            font-size: 13px;
            font-weight: 600;
        }}

        .field-label {{
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 700;
        }}

        .field-input {{
            width: 100%;
            padding: 12px 12px;
            margin-bottom: 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #fff;
            color: var(--text);
            font-size: 14px;
            transition: border-color .15s ease, box-shadow .15s ease;
        }}

        .field-input:focus {{
            outline: none;
            border-color: var(--brand-red);
            box-shadow: 0 0 0 3px rgba(178, 34, 34, 0.12);
        }}

        .submit-btn {{
            width: 100%;
            margin-top: 4px;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: var(--brand-red);
            color: #fff;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 0.2px;
            transition: background .15s ease, transform .05s ease;
        }}

        .submit-btn:hover {{ background: #9a1f1f; }}
        .submit-btn:active {{ transform: translateY(1px); }}
    </style>
</head>
<body>
    <div class="login-shell">
        <div class="login-header">
            <h2 class="login-title">FlagTech</h2>
            <p class="login-subtitle">Sign in to access your shop workspace</p>
        </div>

        <div class="login-body">
            {info_html}
            {error_html}
            <form method="post" action="/auth/login" autocomplete="on">
                <label class="field-label" for="email">Email</label>
                <input class="field-input" id="email" name="email" type="email" required autocomplete="email" />

                <label class="field-label" for="password">Password</label>
                <input class="field-input" id="password" name="password" type="password" required autocomplete="current-password" />

                <button class="submit-btn" type="submit">Sign In</button>
            </form>
        </div>
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

    reason = (request.query_params.get("reason") or "").strip().lower()
    info_message = ""
    if reason == "logged_out":
        info_message = "You have been signed out."
    elif reason == "auth_required":
        info_message = "Please sign in to continue."

    return HTMLResponse(_render_login_page(info=info_message))


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
    response = RedirectResponse(url="/auth/login?reason=logged_out", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie("user_domain", path="/")
    return response
