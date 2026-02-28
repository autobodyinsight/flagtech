from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.auth import (
    ARCHITECT_EMAIL,
    SESSION_COOKIE_NAME,
    build_password_reset_link,
    create_session_for_user,
    create_user,
    delete_session_by_token,
    generate_password_reset_token,
    get_session_by_token,
    get_user_by_email,
    normalize_email,
    send_password_reset_email,
    update_user,
    user_count,
    verify_password_reset_token,
    verify_password,
)

router = APIRouter()


def _render_shell(title: str, subtitle: str, body: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <style>
        :root {{
            --brand-red: #b22222;
            --brand-gray: #3c4142;
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
        .shell {{
            width: 100%;
            max-width: 430px;
            background: var(--surface);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.35);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
            overflow: hidden;
        }}
        .header {{
            padding: 18px 22px;
            background: var(--brand-gray);
            border-bottom: 4px solid var(--brand-red);
        }}
        .title {{ margin: 0; color: #fff; font-size: 24px; font-weight: 700; letter-spacing: 0.3px; }}
        .subtitle {{ margin: 6px 0 0; color: #d6dadd; font-size: 13px; }}
        .body {{ padding: 22px; background: var(--surface-soft); }}
        .banner-error {{ margin-bottom: 14px; padding: 10px 12px; border-radius: 8px; border: 1px solid #e5b4b4; background: #fdecec; color: #8f1b1b; font-size: 13px; font-weight: 600; }}
        .banner-info {{ margin-bottom: 14px; padding: 10px 12px; border-radius: 8px; border: 1px solid #c8d0d4; background: #eef2f4; color: #2f3b3f; font-size: 13px; font-weight: 600; }}
        .field-label {{ display: block; margin-bottom: 6px; font-size: 13px; color: var(--text-muted); font-weight: 700; }}
        .field-input {{ width: 100%; padding: 12px; margin-bottom: 14px; border: 1px solid var(--border); border-radius: 8px; background: #fff; color: var(--text); font-size: 14px; }}
        .field-input:focus {{ outline: none; border-color: var(--brand-red); box-shadow: 0 0 0 3px rgba(178, 34, 34, 0.12); }}
        .submit-btn {{ width: 100%; margin-top: 4px; padding: 12px; border: none; border-radius: 8px; background: var(--brand-red); color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; }}
        .submit-btn:hover {{ background: #9a1f1f; }}
        .switch-link {{ margin-top: 12px; text-align: center; font-size: 13px; color: #555; }}
        .switch-link a {{ color: #b22222; text-decoration: none; font-weight: 700; }}
    </style>
</head>
<body>
    <div class=\"shell\">
        <div class=\"header\">
            <h2 class=\"title\">FlagTech</h2>
            <p class=\"subtitle\">{subtitle}</p>
        </div>
        <div class=\"body\">
            {body}
        </div>
    </div>
</body>
</html>
"""


def _signup_page(error: str = "", info: str = "") -> str:
    error_html = f"<div class='banner-error'>{error}</div>" if error else ""
    info_html = f"<div class='banner-info'>{info}</div>" if info else ""
    body = f"""
        {info_html}
        {error_html}
        <form method=\"post\" action=\"/auth/signup\" autocomplete=\"on\">
            <label class=\"field-label\" for=\"email\">Email</label>
            <input class=\"field-input\" id=\"email\" name=\"email\" type=\"email\" required autocomplete=\"email\" />

            <label class=\"field-label\" for=\"password\">Password</label>
            <input class=\"field-input\" id=\"password\" name=\"password\" type=\"password\" required autocomplete=\"new-password\" />

            <label class=\"field-label\" for=\"confirm_password\">Confirm Password</label>
            <input class=\"field-input\" id=\"confirm_password\" name=\"confirm_password\" type=\"password\" required autocomplete=\"new-password\" />

            <button class=\"submit-btn\" type=\"submit\">Create Account</button>
        </form>
        <div class=\"switch-link\">Already have an account? <a href=\"/auth/login\">Log In</a></div>
    """
    return _render_shell("FlagTech Sign-Up", "Create your account", body)


def _login_page(error: str = "", info: str = "") -> str:
    error_html = f"<div class='banner-error'>{error}</div>" if error else ""
    info_html = f"<div class='banner-info'>{info}</div>" if info else ""
    body = f"""
        {info_html}
        {error_html}
        <form method=\"post\" action=\"/auth/login\" autocomplete=\"on\">
            <label class=\"field-label\" for=\"email\">Email</label>
            <input class=\"field-input\" id=\"email\" name=\"email\" type=\"email\" required autocomplete=\"email\" />

            <label class=\"field-label\" for=\"password\">Password</label>
            <input class=\"field-input\" id=\"password\" name=\"password\" type=\"password\" required autocomplete=\"current-password\" />

            <button class=\"submit-btn\" type=\"submit\">Sign In</button>
        </form>
            <div class=\"switch-link\"><a href=\"/auth/forgot-password\">Forgot password?</a></div>
            <div class=\"switch-link\">No account yet? <a href=\"/auth/signup\">Sign Up</a></div>
    """
    return _render_shell("FlagTech Login", "Sign in to continue", body)


def _forgot_password_page(error: str = "", info: str = "") -> str:
    error_html = f"<div class='banner-error'>{error}</div>" if error else ""
    info_html = f"<div class='banner-info'>{info}</div>" if info else ""
    body = f"""
        {info_html}
        {error_html}
        <form method="post" action="/auth/forgot-password" autocomplete="on">
            <label class="field-label" for="email">Email</label>
            <input class="field-input" id="email" name="email" type="email" required autocomplete="email" />

            <button class="submit-btn" type="submit">Send Reset Link</button>
        </form>
        <div class="switch-link"><a href="/auth/login">Back to login</a></div>
    """
    return _render_shell("Forgot Password", "Request a reset link", body)


def _reset_password_page(token: str, error: str = "", info: str = "") -> str:
    error_html = f"<div class='banner-error'>{error}</div>" if error else ""
    info_html = f"<div class='banner-info'>{info}</div>" if info else ""
    body = f"""
        {info_html}
        {error_html}
        <form method="post" action="/auth/reset-password" autocomplete="on">
            <input type="hidden" name="token" value="{token}" />

            <label class="field-label" for="password">New Password</label>
            <input class="field-input" id="password" name="password" type="password" required autocomplete="new-password" />

            <label class="field-label" for="confirm_password">Confirm Password</label>
            <input class="field-input" id="confirm_password" name="confirm_password" type="password" required autocomplete="new-password" />

            <button class="submit-btn" type="submit">Reset Password</button>
        </form>
        <div class="switch-link"><a href="/auth/login">Back to login</a></div>
    """
    return _render_shell("Reset Password", "Set a new password", body)

@router.get("/auth/start")
async def auth_start(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    session = get_session_by_token(token)
    if session:
        return RedirectResponse(url="/ui/", status_code=303)
    if user_count() == 0:
        return RedirectResponse(url="/auth/signup", status_code=303)
    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/auth/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    if user_count() > 0:
        return HTMLResponse(_signup_page(info="Create an additional user account."))
    return HTMLResponse(_signup_page(info="No users found. Create the first account."))


@router.post("/auth/signup", response_class=HTMLResponse)
async def signup_submit(
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    normalized_email = normalize_email(email)
    if password != confirm_password:
        return HTMLResponse(_signup_page(error="Passwords do not match."), status_code=400)
    if len(password) < 8:
        return HTMLResponse(_signup_page(error="Password must be at least 8 characters."), status_code=400)

    try:
        create_user(
            email=normalized_email,
            password=password,
            role="user",
        )
    except ValueError as exc:
        return HTMLResponse(_signup_page(error=str(exc)), status_code=400)
    except Exception as exc:
        return HTMLResponse(_signup_page(error=f"Unable to sign up: {exc}"), status_code=500)

    return RedirectResponse(url="/auth/login?reason=signed_up", status_code=303)


@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    session = get_session_by_token(token) if token else None
    if session:
        return RedirectResponse(url="/ui/", status_code=303)

    reason = (request.query_params.get("reason") or "").strip().lower()
    info_message = ""
    if reason == "signed_up":
        info_message = "Account created. Please sign in."
    elif reason == "logged_out":
        info_message = "You have been signed out."
    elif reason == "password_reset":
        info_message = "Password updated. Please sign in."
    return HTMLResponse(_login_page(info=info_message))


@router.get("/auth/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return HTMLResponse(_forgot_password_page())


@router.post("/auth/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(email: str = Form(...)):
    normalized_email = normalize_email(email)
    user = get_user_by_email(normalized_email)

    generic_message = "If an account exists for this email, a reset link has been sent."
    if not user or not user.get("active"):
        return HTMLResponse(_forgot_password_page(info=generic_message))

    try:
        token = generate_password_reset_token(user)
        reset_link = build_password_reset_link(token)
        send_password_reset_email(normalized_email, reset_link)
        return HTMLResponse(_forgot_password_page(info=generic_message))
    except Exception:
        return HTMLResponse(
            _forgot_password_page(error="Unable to send reset email right now. Please try again later."),
            status_code=500,
        )


@router.get("/auth/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    token = (request.query_params.get("token") or "").strip()
    if not token:
        return HTMLResponse(_forgot_password_page(error="Invalid reset link."), status_code=400)

    user = verify_password_reset_token(token)
    if not user:
        return HTMLResponse(_forgot_password_page(error="This reset link is invalid or expired."), status_code=400)
    return HTMLResponse(_reset_password_page(token=token))


@router.post("/auth/reset-password", response_class=HTMLResponse)
async def reset_password_submit(
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    token = (token or "").strip()
    if not token:
        return HTMLResponse(_forgot_password_page(error="Invalid reset link."), status_code=400)

    user = verify_password_reset_token(token)
    if not user:
        return HTMLResponse(_forgot_password_page(error="This reset link is invalid or expired."), status_code=400)

    if password != confirm_password:
        return HTMLResponse(_reset_password_page(token=token, error="Passwords do not match."), status_code=400)
    if len(password) < 8:
        return HTMLResponse(
            _reset_password_page(token=token, error="Password must be at least 8 characters."),
            status_code=400,
        )

    updated = update_user(user_id=int(user.get("id")), password=password)
    if not updated:
        return HTMLResponse(_forgot_password_page(error="Unable to reset password."), status_code=500)

    return RedirectResponse(url="/auth/login?reason=password_reset", status_code=303)


@router.post("/auth/login", response_class=HTMLResponse)
async def login_submit(email: str = Form(...), password: str = Form(...)):
    normalized_email = normalize_email(email)
    user = get_user_by_email(normalized_email)

    if not user or not user.get("active"):
        return HTMLResponse(_login_page(error="Invalid email or password."), status_code=401)

    if not verify_password(password, user.get("password_hash") or ""):
        return HTMLResponse(_login_page(error="Invalid email or password."), status_code=401)

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
        value=user.get("domain") or normalize_email(user.get("email", "")).split("@", 1)[-1],
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
    return response


@router.get("/auth/whoami")
async def whoami(request: Request):
    user = getattr(request.state, "user", None) or {}
    email = normalize_email(user.get("email"))
    return {
        "email": email,
        "role": user.get("role") or "user",
        "is_architect": email == ARCHITECT_EMAIL or (str(user.get("role") or "").strip().lower() == "architect"),
    }
