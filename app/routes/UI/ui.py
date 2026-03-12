"""Main UI display for FlagTech - simplified version with just the display screen."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from .flagout import get_flagtech_screen_html
from .parts import get_parts_screen_html, get_parts_script
from .dashboard import get_dashboard_screen_html
from .techs import get_techs_screen_html
from .phase import get_phase_screen_html
from .reports import get_reports_screen_html
from .records import get_records_screen_html
from .setup import get_setup_screen_html, get_setup_script

try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html


router = APIRouter()


def _is_authenticated(request: Request) -> bool:
    email = str(request.cookies.get("user_email") or "").strip()
    domain = str(request.cookies.get("user_domain") or "").strip()
    return bool(email and domain)


@router.get("/login", response_class=HTMLResponse)
async def login_screen(request: Request):
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AutobodyOS Login</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #000000 0%, #b22222 100%);
            color: #ffffff;
            overflow: hidden;
        }
        .login-shell {
            min-height: 100vh;
            width: min(92vw, 560px);
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
        }
        .title {
            color: #b22222;
            font-size: clamp(34px, 5.2vw, 52px);
            letter-spacing: 1px;
            font-weight: 700;
            line-height: 1;
        }
        .login-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .login-brand-logo {
            width: clamp(44px, 6vw, 56px);
            height: clamp(44px, 6vw, 56px);
            border-radius: 10px;
            object-fit: contain;
            background: rgba(255, 255, 255, 0.9);
            padding: 4px;
        }
        .subtitle {
            color: rgba(255, 255, 255, 0.86);
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        .login-form {
            display: flex;
            flex-direction: column;
            gap: 22px;
            margin-top: 10px;
        }
        .field {
            position: relative;
            width: 100%;
        }
        .field input {
            width: 100%;
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.6);
            background: transparent;
            color: #ffffff;
            font-size: 18px;
            padding: 18px 2px 10px;
            outline: none;
            transition: border-color 0.2s ease;
        }
        .field input:focus {
            border-bottom-color: #ffffff;
        }
        .field label {
            position: absolute;
            left: 2px;
            top: 16px;
            color: rgba(255, 255, 255, 0.72);
            pointer-events: none;
            transition: all 0.18s ease;
            letter-spacing: 0.3px;
        }
        .field input:focus + label,
        .field input:not(:placeholder-shown) + label {
            top: -2px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.92);
        }
        .btn {
            display: block;
            width: fit-content;
            min-width: 170px;
            border: 1px solid rgba(255, 255, 255, 0.55);
            border-radius: 999px;
            padding: 11px 24px;
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            letter-spacing: 0.5px;
            transition: transform 0.16s ease, background 0.16s ease, border-color 0.16s ease;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.16);
            border-color: #ffffff;
            transform: translateY(-1px);
        }
        .btn:disabled {
            opacity: 0.7;
            cursor: default;
            transform: none;
        }
        .error {
            min-height: 22px;
            color: #ffd5d5;
            font-size: 13px;
            letter-spacing: 0.2px;
        }
        @media (max-width: 640px) {
            .login-shell {
                width: min(92vw, 480px);
                padding-bottom: 30px;
            }
            .field input {
                font-size: 17px;
            }
        }
    </style>
</head>
<body>
    <div class="login-shell">
        <div class="login-brand">
            <img class="login-brand-logo" src="/static/autobodyos.png" alt="AutobodyOS logo" />
            <h1 class="title">AutobodyOS</h1>
        </div>
        <div class="subtitle">Sign in to continue</div>
        <div id="loginError" class="error"></div>
        <form id="loginForm" class="login-form">
            <div class="field">
                <input id="loginEmail" name="loginEmail" type="email" autocomplete="username" placeholder=" " required />
                <label for="loginEmail">Email</label>
            </div>

            <div class="field">
                <input id="loginPassword" name="loginPassword" type="password" autocomplete="current-password" placeholder=" " required />
                <label for="loginPassword">Password</label>
            </div>

            <button id="loginBtn" class="btn" type="submit">Sign In</button>
        </form>
    </div>

    <script>
        const form = document.getElementById('loginForm');
        const errorWrap = document.getElementById('loginError');
        const loginBtn = document.getElementById('loginBtn');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            errorWrap.textContent = '';
            loginBtn.disabled = true;
            try {
                const payload = {
                    email: (document.getElementById('loginEmail').value || '').trim(),
                    password: (document.getElementById('loginPassword').value || ''),
                };

                const resp = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (!resp.ok || data.error) {
                    throw new Error(data.error || 'Login failed');
                }

                window.location.href = '/ui/';
            } catch (error) {
                errorWrap.textContent = String(error.message || 'Login failed');
            } finally {
                loginBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def home_screen(request: Request):
    """Main UI screen with sidebar navigation."""

    if not _is_authenticated(request):
        return RedirectResponse(url="/ui/login")

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>AutobodyOS</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #d3d3d3;
            margin: 0;
        }}
        .app-header {{
            height: 60px;
            min-height: 60px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            background: linear-gradient(90deg, #000000 0%, #b22222 100%);
            color: #fff;
            position: relative;
            z-index: 1200;
        }}
        .app-header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }}
        .app-header-right {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-icon-btn {{
            width: 40px;
            height: 40px;
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 10px;
            background: rgba(255,255,255,0.08);
            color: #fff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 0;
        }}
        .header-icon-btn:hover {{
            background: rgba(255,255,255,0.16);
        }}
        .app-brand-logo {{
            width: 32px;
            height: 32px;
            object-fit: contain;
            border-radius: 6px;
            background: rgba(255,255,255,0.92);
            padding: 2px;
        }}
        .app-brand-text {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0.4px;
            white-space: nowrap;
        }}
        #headerUserButton {{
            width: 40px;
            height: 40px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.35);
            background: rgba(255,255,255,0.14);
            color: #fff;
            font-weight: 800;
            cursor: pointer;
        }}
        #headerUserDropdown {{
            position: absolute;
            top: 48px;
            right: 0;
            min-width: 170px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.18);
            padding: 6px;
            display: none;
            z-index: 1250;
        }}
        .header-menu-action {{
            width: 100%;
            text-align: left;
            border: none;
            background: #fff;
            color: #222;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }}
        .header-menu-action:hover {{
            background: #f3f3f3;
        }}
        #sideNavSidebar {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 64px;
            height: calc(100vh - 60px);
            background: #971d1d;
            box-shadow: 2px 0 18px rgba(0,0,0,0.2);
            transition: width 0.22s ease;
            z-index: 1210;
            padding: 14px 8px;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        #sideNavSidebar.expanded {{
            width: 240px;
        }}
        .side-menu-list {{
            display: grid;
            gap: 6px;
        }}
        .side-menu-item {{
            width: 100%;
            border: none;
            background: transparent;
            color: #ffffff;
            border-radius: 10px;
            padding: 12px 10px;
            text-align: left;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
        }}
        .side-menu-item .nav-icon {{
            width: 24px;
            height: 24px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 24px;
        }}
        .side-menu-item .nav-icon svg {{
            width: 22px;
            height: 22px;
            display: block;
        }}
        .side-menu-item .nav-label {{
            opacity: 0;
            max-width: 0;
            white-space: nowrap;
            overflow: hidden;
            transition: opacity 0.16s ease, max-width 0.2s ease;
        }}
        #sideNavSidebar.expanded .side-menu-item .nav-label {{
            opacity: 1;
            max-width: 160px;
        }}
        .side-menu-item:hover {{
            background: #9f1e1e;
            color: #ffffff;
        }}
        .side-menu-item.active {{
            background: #b22222;
            color: #ffffff;
            text-decoration: none;
            box-shadow: inset 4px 0 0 #ffffff;
        }}
        .side-menu-item:last-child {{
            border-bottom: none;
        }}
        .header-modal-shell {{
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.38);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1320;
            padding: 18px;
        }}
        .header-modal-card {{
            width: min(860px, 96vw);
            max-height: 86vh;
            overflow: auto;
            background: #fff;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 16px 34px rgba(0,0,0,0.26);
        }}
        .header-chat-layout {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }}
        #chatModal {{
            padding: 0;
            align-items: stretch;
            justify-content: stretch;
        }}
        #chatModal .header-modal-card {{
            width: 100vw;
            max-width: none;
            height: 100vh;
            max-height: none;
            border-radius: 0;
            display: flex;
            flex-direction: column;
            padding: 18px 22px;
            overflow: hidden;
        }}
        #chatModal .header-chat-layout {{
            flex: 1;
            min-height: 0;
            display: grid;
            grid-template-columns: 1fr 1fr 1.35fr;
            gap: 0;
            align-items: stretch;
            border-top: 1px solid #e7e1de;
            border-bottom: 1px solid #e7e1de;
        }}
        .chat-task-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 12px;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }}
        .chat-task-scroll {{
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding-right: 2px;
        }}
        .chat-user-panel,
        .chat-window-panel {{
            min-height: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #fff;
            border: none;
            border-radius: 0;
            padding: 0;
        }}
        .chat-user-panel {{
            border-left: 1px solid #ece6e3;
            border-right: 1px solid #ece6e3;
        }}
        .chat-column-header {{
            height: 54px;
            display: flex;
            align-items: center;
            padding: 0 14px;
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 0.2px;
            color: #2b2b2b;
            border-bottom: 1px solid #ece6e3;
            background: #fcfbfb;
        }}
        .chat-main-grid {{
            flex: 1;
            min-height: 0;
            display: grid;
            grid-template-columns: 1fr 1fr 1.35fr;
            border-top: 1px solid #e7e1de;
            border-bottom: 1px solid #e7e1de;
            background: #fff;
        }}
        .chat-bottom-strip {{
            margin-top: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 12px;
            background: #fafafa;
            min-height: 130px;
            max-height: 24vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .chat-user-list {{
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            background: #f8f8f8;
        }}
        .chat-user-row {{
            width: 100%;
            border: none;
            border-bottom: 1px solid #ebe7e5;
            background: #f7f6f6;
            color: #222;
            text-align: left;
            padding: 12px 10px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 3px solid transparent;
            transition: background 0.15s ease, border-color 0.15s ease;
        }}
        .chat-user-row:hover {{
            background: #f1eeee;
        }}
        .chat-user-row.active {{
            background: #f9efef;
            border-left-color: #b22222;
        }}
        .chat-user-row.unread {{
            font-weight: 800;
        }}
        .chat-user-avatar {{
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: #ece8e6;
            color: #333;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 800;
            flex: 0 0 28px;
        }}
        .chat-user-label {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-message-scroll {{
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding: 14px 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: #f3f2f2;
        }}
        .chat-bubble {{
            max-width: 74%;
            border-radius: 16px;
            padding: 9px 12px;
            font-size: 14px;
            line-height: 1.35;
            border: 1px solid transparent;
        }}
        .chat-bubble.sender {{
            margin-left: auto;
            background: #b22222;
            color: #fff;
            border-top-right-radius: 6px;
        }}
        .chat-bubble.receiver {{
            margin-right: auto;
            background: #ffffff;
            color: #222;
            border-color: #e3dedb;
            border-top-left-radius: 6px;
        }}
        .chat-window-head {{
            min-height: 54px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 0 14px;
            border-bottom: 1px solid #ece6e3;
            background: #ffffff;
        }}
        .chat-window-title {{
            font-size: 16px;
            font-weight: 800;
            color: #262626;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-window-input-wrap {{
            border-top: 1px solid #ece6e3;
            background: #fff;
            padding: 10px 12px;
            display: grid;
            gap: 8px;
        }}
        .chat-task-send-row {{
            display: flex;
            justify-content: flex-end;
        }}
        .chat-task-send-btn {{
            border: 1px solid #b22222;
            background: #fff;
            color: #b22222;
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
        }}
        .chat-input-row {{
            display: flex;
            align-items: stretch;
            gap: 8px;
        }}
        .chat-text-input {{
            flex: 1;
            min-height: 46px;
            max-height: 96px;
            border: 1px solid #d8d1ce;
            border-radius: 999px;
            padding: 12px 16px;
            resize: none;
            font-size: 14px;
            line-height: 1.25;
            outline: none;
            background: #fff;
        }}
        .chat-text-input:focus {{
            border-color: #b22222;
            box-shadow: 0 0 0 2px rgba(178, 34, 34, 0.12);
        }}
        .chat-send-btn {{
            width: 46px;
            height: 46px;
            border: none;
            border-radius: 999px;
            background: #b22222;
            color: #fff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            flex: 0 0 46px;
        }}
        .chat-send-btn:hover {{
            filter: brightness(0.95);
        }}
        @media (max-width: 840px) {{
            .content-area {{ padding: 18px; }}
            .app-brand-text {{ font-size: 18px; }}
            #sideNavSidebar {{ width: 56px; }}
            #sideNavSidebar.expanded {{ width: 220px; }}
            .content-area {{ margin-left: 56px; }}
            .chat-main-grid {{
                grid-template-columns: 1fr;
                overflow-y: auto;
            }}
            .chat-user-panel {{
                border-left: none;
                border-right: none;
                border-top: 1px solid #ece6e3;
                border-bottom: 1px solid #ece6e3;
            }}
            .chat-window-panel {{
                min-height: 340px;
            }}
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
            margin-left: 64px;
            overflow-y: auto;
            background-color: #d3d3d3;
        }}
        .screen {{
            display: none;
        }}
        .screen.active {{
            display: block;
        }}
        :root {{
            --app-bg: #d3d3d3;
            --card-bg: #f2f0ef;
            --brand-red: #b22222;
            --tab-inactive: #3c4142;
        }}
        body,
        .content-area,
        .screen {{
            background-color: var(--app-bg) !important;
        }}
        [style*="background:#d32f2f"],
        [style*="background: #d32f2f"],
        [style*="background-color:#d32f2f"],
        [style*="background-color: #d32f2f"],
        [style*="background:#b22222"],
        [style*="background: #b22222"],
        [style*="background-color:#b22222"],
        [style*="background-color: #b22222"],
        [style*="background:#505050"],
        [style*="background: #505050"],
        [style*="background-color:#505050"],
        [style*="background-color: #505050"],
        [style*="background:#666666"],
        [style*="background: #666666"],
        [style*="background-color:#666666"],
        [style*="background-color: #666666"],
        [style*="background:#707070"],
        [style*="background: #707070"],
        [style*="background-color:#707070"],
        [style*="background-color: #707070"] {{
            background: var(--brand-red) !important;
            background-color: var(--brand-red) !important;
        }}
        button:not([style*="background:none"]):not([style*="background: none"]):not(.link-button):not(.tech-link):not(.header-icon-btn):not(.side-menu-item):not(.header-menu-action) {{
            background: var(--brand-red) !important;
            background-color: var(--brand-red) !important;
            color: #fff !important;
        }}
        button[style*="background:none"],
        button[style*="background: none"],
        .link-button,
        .tech-link {{
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            border-radius: 0 !important;
            color: #007bff !important;
            box-shadow: none !important;
        }}
        button[style*="background:none"]:hover,
        button[style*="background: none"]:hover,
        .link-button:hover,
        .tech-link:hover {{
            background: transparent !important;
            background-color: transparent !important;
            text-decoration: underline !important;
        }}
        .nav-tab {{
            background-color: var(--tab-inactive) !important;
            color: #fff !important;
            opacity: 1 !important;
            background-image: none !important;
            box-shadow: none !important;
            filter: none !important;
        }}
        .nav-tab.active {{
            background-color: var(--brand-red) !important;
            border-bottom-color: var(--brand-red) !important;
        }}
        .tab-button {{
            background-color: var(--tab-inactive) !important;
            color: #fff !important;
        }}
        .tab-button.active {{
            background-color: var(--brand-red) !important;
        }}
        .modal-content,
        .dash-center-card,
        .dash-mini-card,
        .mini-popup-panel,
        .phase-card,
        #estimateSummary,
        #flagoutTechTable,
        #techsTableContainer,
        #statusDropdownMenu,
        [style*="background:#fff"],
        [style*="background: #fff"],
        [style*="background-color:#fff"],
        [style*="background-color: #fff"],
        [style*="background:#f9f9f9"],
        [style*="background: #f9f9f9"],
        [style*="background-color:#f9f9f9"],
        [style*="background-color: #f9f9f9"],
        [style*="background:#f2f2f2"],
        [style*="background: #f2f2f2"],
        [style*="background-color:#f2f2f2"],
        [style*="background-color: #f2f2f2"],
        [style*="background:#f0f0f0"],
        [style*="background: #f0f0f0"],
        [style*="background-color:#f0f0f0"],
        [style*="background-color: #f0f0f0"],
        [style*="background:#f5f5f5"],
        [style*="background: #f5f5f5"],
        [style*="background-color:#f5f5f5"],
        [style*="background-color: #f5f5f5"],
        [style*="background:#f7f7f7"],
        [style*="background: #f7f7f7"],
        [style*="background-color:#f7f7f7"],
        [style*="background-color: #f7f7f7"],
        [style*="background:#fafafa"],
        [style*="background: #fafafa"],
        [style*="background-color:#fafafa"],
        [style*="background-color: #fafafa"],
        [style*="background:#e0e0e0"],
        [style*="background: #e0e0e0"],
        [style*="background-color:#e0e0e0"],
        [style*="background-color: #e0e0e0"],
        [style*="background:#d9d9d9"],
        [style*="background: #d9d9d9"],
        [style*="background-color:#d9d9d9"],
        [style*="background-color: #d9d9d9"] {{
            background: var(--card-bg) !important;
            background-color: var(--card-bg) !important;
        }}
        .phase-cards {{
            background: transparent !important;
            background-color: transparent !important;
        }}
    </style>
</head>
<body>
    <header class="app-header">
        <div class="app-header-left">
            <img class="app-brand-logo" src="/static/autobodyos.png" alt="AutobodyOS logo" />
            <div class="app-brand-text">AutobodyOS</div>
        </div>
        <div class="app-header-right">
            <div style="position:relative;">
                <button id="headerUserButton" type="button" aria-label="Open user menu">--</button>
                <div id="headerUserDropdown">
                    <button type="button" class="header-menu-action" onclick="openProfileModal()">Profile</button>
                    <button type="button" class="header-menu-action" onclick="logoutApp()">Log Out</button>
                </div>
            </div>
        </div>
    </header>

    <aside id="sideNavSidebar" aria-label="Primary navigation">
        <div class="side-menu-list">
            <button type="button" class="side-menu-item active" data-screen="dashboard" aria-label="Dashboard"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 13h6v7H4v-7zm10-9h6v16h-6V4zM4 4h6v7H4V4z" stroke="currentColor" stroke-width="1.8"/></svg></span><span class="nav-label">Dashboard</span></button>
            <button type="button" class="side-menu-item" data-screen="upload" aria-label="Upload"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16V4m0 0l-4 4m4-4l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M4 20h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span><span class="nav-label">Upload</span></button>
            <button type="button" class="side-menu-item" data-screen="phase" aria-label="Roadmap"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 6h8M4 12h16M4 18h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span><span class="nav-label">Roadmap</span></button>
            <button type="button" class="side-menu-item" data-screen="parts" aria-label="Parts"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="8" cy="18" r="2" stroke="currentColor" stroke-width="1.8"/><circle cx="17" cy="18" r="2" stroke="currentColor" stroke-width="1.8"/><path d="M4 6h2l2 9h10l2-7H8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="nav-label">Parts</span></button>
            <button type="button" class="side-menu-item" data-screen="tech" aria-label="Techs"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="3" stroke="currentColor" stroke-width="1.8"/><path d="M5 20c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span><span class="nav-label">Techs</span></button>
            <button type="button" class="side-menu-item" data-screen="flagtech" aria-label="Flagout"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 3v18" stroke="currentColor" stroke-width="1.8"/><path d="M6 4h11l-2.2 3L17 10H6" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg></span><span class="nav-label">Flagout</span></button>
            <button type="button" class="side-menu-item" data-screen="reports" aria-label="Reports"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 5h14v14H5z" stroke="currentColor" stroke-width="1.8"/><path d="M8 9h8M8 13h8M8 17h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span><span class="nav-label">Reports</span></button>
            <button type="button" class="side-menu-item" data-screen="setup" aria-label="Setup"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4z" stroke="currentColor" stroke-width="1.8"/><path d="M19.4 15l1.6 1-1.5 2.6-1.8-.6a7.8 7.8 0 0 1-1.4.8l-.3 1.9h-3l-.3-1.9a7.8 7.8 0 0 1-1.4-.8l-1.8.6L3 16l1.6-1a7.7 7.7 0 0 1 0-2l-1.6-1L4.5 9.4l1.8.6a7.8 7.8 0 0 1 1.4-.8l.3-1.9h3l.3 1.9a7.8 7.8 0 0 1 1.4.8l1.8-.6L21 12l-1.6 1a7.7 7.7 0 0 1 0 2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg></span><span class="nav-label">Setup</span></button>
            <button type="button" class="side-menu-item" data-action="chat" aria-label="Chat"><span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 5h16v10H8l-4 4V5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg></span><span class="nav-label">Chat</span></button>
        </div>
    </aside>

    <div id="chatModal" class="header-modal-shell">
        <div class="header-modal-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#333;">Messages & Tasks</h3>
                <button type="button" class="header-menu-action" style="width:auto;" onclick="closeChatModal()">Close</button>
            </div>
            <div class="chat-main-grid">
                <div class="chat-task-card" style="margin:0;">
                    <div class="chat-column-header" style="padding-left:0; padding-right:0; background:transparent; border-bottom:none; height:auto; margin-bottom:8px;">Task List</div>
                    <div class="chat-task-scroll" style="border-top:1px solid #ebe6e3; border-bottom:1px solid #ebe6e3; padding-top:6px; padding-bottom:6px;">
                        <div id="chatTaskList" style="display:flex; flex-direction:column; gap:8px; color:#333;">NO TASK</div>
                    </div>
                </div>
                <div class="chat-user-panel">
                    <div class="chat-column-header">User List</div>
                    <div id="chatUserList" class="chat-user-list"></div>
                    <select id="chatUserSelect" style="display:none;"></select>
                </div>
                <div class="chat-window-panel">
                    <div class="chat-window-head">
                        <div id="chatSelectedUserName" class="chat-window-title">Select a user</div>
                    </div>
                    <div id="chatMessagesArea" class="chat-message-scroll">
                        <div style="color:#666;">No messages yet.</div>
                    </div>
                    <div class="chat-window-input-wrap">
                        <div class="chat-task-send-row">
                            <button type="button" class="chat-task-send-btn" onclick="sendHeaderMessage('task')">Send Task</button>
                        </div>
                        <div class="chat-input-row">
                            <textarea id="chatMessageText" class="chat-text-input" rows="2" placeholder="Write a message..."></textarea>
                            <button type="button" class="chat-send-btn" onclick="sendChatPanelMessage()" aria-label="Send message">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                                    <path d="M3 11.5L20.5 3.5L14 20.5L11 13.5L3 11.5Z" fill="currentColor"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div id="chatSendStatus" style="min-height:18px; margin:0 12px 10px 12px; font-size:12px; color:#444;"></div>
                </div>
            </div>
            <div class="chat-bottom-strip">
                <div style="font-weight:800; letter-spacing:0.6px; margin-bottom:8px;">COMPLETED</div>
                <div class="chat-task-scroll">
                    <div id="chatCompletedList" style="display:flex; flex-direction:column; gap:8px; color:#333;">NO COMPLETED TASKS</div>
                </div>
            </div>
        </div>
    </div>

    <div id="profileModal" class="header-modal-shell">
        <div class="header-modal-card" style="width:min(520px, 96vw);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#333;">Profile</h3>
                <button type="button" class="header-menu-action" style="width:auto;" onclick="closeProfileModal()">Close</button>
            </div>
            <div style="display:grid; grid-template-columns:1fr; gap:10px; color:#222;">
                <div><strong>Shop association:</strong> <span id="profileShopText">-</span></div>
                <div><strong>Role:</strong> <span id="profileRoleText">-</span></div>
                <div><strong>Email:</strong> <span id="profileEmailText">-</span></div>
            </div>
            <div style="margin-top:14px;">
                <button id="profileResetPasswordBtn" type="button" class="header-menu-action" style="width:auto; background:#b22222; color:#fff;" onclick="resetProfilePassword()">Reset Password</button>
            </div>
        </div>
    </div>
    
    <div class="content-area">
        {get_dashboard_screen_html()}
        {get_upload_screen_html()}
        {get_estimate_summary_html()}
        {get_parts_screen_html()}
        {get_techs_screen_html()}
        {get_phase_screen_html()}
        {get_flagtech_screen_html()}
        {get_reports_screen_html()}
        {get_records_screen_html()}
        {get_setup_screen_html()}
    </div>
    
    <script>
        function normalizeFormAccessibility(root = document) {{
            const fields = root.querySelectorAll('input, select, textarea');
            let counter = window.__flagtechFieldCounter || 0;

            fields.forEach((field) => {{
                const type = (field.getAttribute('type') || '').toLowerCase();
                if (!field.id) {{
                    counter += 1;
                    field.id = `ft-field-${{counter}}`;
                }}
                if (!field.name && !['button', 'submit', 'reset', 'image'].includes(type)) {{
                    field.name = field.id;
                }}
            }});

            window.__flagtechFieldCounter = counter;

            const labels = Array.from(root.querySelectorAll('label'));
            labels.forEach((label) => {{
                if (label.htmlFor) return;

                let target = label.querySelector('input, select, textarea');
                if (!target && label.nextElementSibling && label.nextElementSibling.matches('input, select, textarea')) {{
                    target = label.nextElementSibling;
                }}

                if (target) {{
                    if (!target.id) {{
                        counter += 1;
                        target.id = `ft-field-${{counter}}`;
                    }}
                    label.htmlFor = target.id;
                }}
            }});

            window.__flagtechFieldCounter = counter;
        }}

        normalizeFormAccessibility();
        const a11yObserver = new MutationObserver(() => normalizeFormAccessibility());
        a11yObserver.observe(document.body, {{ childList: true, subtree: true }});

        const appUiState = {{
            activeScreen: 'dashboard',
            sessionUser: null,
            shopDomain: '',
            shopName: '',
            users: [],
            currentUser: null,
            chatTasks: [],
            completedTasks: [],
            chatConversations: {{}},
            chatSelectedUserId: '',
            chatUnreadUserIds: [],
            chatLastActivityByUser: {{}},
            chatMessages: [],
            chatPollTimer: null,
        }};

        async function fetchChatMessages() {{
            const response = await fetch('/api/chat/messages', {{ credentials: 'include' }});
            const data = await response.json();
            if (!response.ok || data.error) throw new Error(data.error || 'Unable to load chat messages');
            appUiState.chatMessages = Array.isArray(data.messages) ? data.messages : [];
        }}

        function deriveChatStateFromMessages() {{
            const currentUserId = String(appUiState.currentUser?.id || '');
            const convoMap = {{}};
            const lastActivity = {{}};
            const unreadSet = new Set();
            const openTasks = [];
            const doneTasks = [];

            if (!currentUserId) {{
                appUiState.chatConversations = {{}};
                appUiState.chatUnreadUserIds = [];
                appUiState.chatLastActivityByUser = {{}};
                appUiState.chatTasks = [];
                appUiState.completedTasks = [];
                return;
            }}

            (Array.isArray(appUiState.chatMessages) ? appUiState.chatMessages : []).forEach((row) => {{
                const fromId = String(row?.from_user_id || '');
                const toId = String(row?.to_user_id || '');
                if (!fromId || !toId) return;
                if (fromId !== currentUserId && toId !== currentUserId) return;

                const otherId = fromId === currentUserId ? toId : fromId;
                const ts = Number(row?.ts || 0) || Date.now();
                if (!lastActivity[otherId] || ts > lastActivity[otherId]) lastActivity[otherId] = ts;

                const kind = String(row?.kind || 'message');
                if (kind === 'task') {{
                    if (toId === currentUserId) {{
                        const taskRow = {{
                            id: Number(row?.id || 0),
                            text: String(row?.text || ''),
                            ts,
                            fromUserId: fromId,
                        }};
                        if (row?.completed_at) doneTasks.push(taskRow);
                        else openTasks.push(taskRow);
                    }}
                    return;
                }}

                if (!convoMap[otherId]) convoMap[otherId] = [];
                convoMap[otherId].push({{
                    side: fromId === currentUserId ? 'sender' : 'receiver',
                    text: String(row?.text || ''),
                    ts,
                }});

                if (toId === currentUserId && !row?.read_at) unreadSet.add(otherId);
            }});

            Object.keys(convoMap).forEach((otherId) => {{
                convoMap[otherId].sort((a, b) => Number(a.ts || 0) - Number(b.ts || 0));
            }});

            openTasks.sort((a, b) => Number(b.ts || 0) - Number(a.ts || 0));
            doneTasks.sort((a, b) => Number(b.ts || 0) - Number(a.ts || 0));

            const unreadIds = Array.from(unreadSet);

            unreadIds.sort((a, b) => (lastActivity[b] || 0) - (lastActivity[a] || 0));
            appUiState.chatConversations = convoMap;
            appUiState.chatUnreadUserIds = unreadIds;
            appUiState.chatLastActivityByUser = lastActivity;
            appUiState.chatTasks = openTasks;
            appUiState.completedTasks = doneTasks;

            if (appUiState.chatSelectedUserId && !appUiState.users.some((u) => String(u?.id || '') === String(appUiState.chatSelectedUserId))) {{
                appUiState.chatSelectedUserId = '';
            }}
        }}

        async function markConversationRead(userId) {{
            const currentUserId = String(appUiState.currentUser?.id || '');
            const otherId = String(userId || '');
            if (!currentUserId || !otherId) return;

            try {{
                await fetch('/api/chat/read', {{
                    method: 'POST',
                    credentials: 'include',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ with_user_id: Number(otherId) }}),
                }});
            }} catch (error) {{
                console.error('Unable to mark conversation as read:', error);
            }}

            appUiState.chatUnreadUserIds = appUiState.chatUnreadUserIds.filter((id) => String(id) !== otherId);
        }}

        function headerEscapeHtml(value) {{
            return String(value === null || value === undefined ? '' : value)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }}

        async function completeChatTaskAt(index) {{
            const parsed = Number(index);
            if (!Number.isInteger(parsed) || parsed < 0 || parsed >= appUiState.chatTasks.length) return;
            const task = appUiState.chatTasks[parsed];
            if (!task?.id) return;
            try {{
                const response = await fetch('/api/chat/task/complete', {{
                    method: 'POST',
                    credentials: 'include',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ task_id: Number(task.id) }}),
                }});
                const data = await response.json();
                if (!response.ok || data.error) throw new Error(data.error || 'Unable to complete task');
                await fetchChatMessages();
                deriveChatStateFromMessages();
                renderChatTaskPanels();
                renderChatUserList();
                renderChatConversation();
            }} catch (error) {{
                alert(String(error.message || 'Unable to complete task'));
            }}
        }}

        function renderChatTaskPanels() {{
            const listEl = document.getElementById('chatTaskList');
            const completedEl = document.getElementById('chatCompletedList');
            if (!listEl || !completedEl) return;

            if (!Array.isArray(appUiState.chatTasks) || appUiState.chatTasks.length === 0) {{
                listEl.innerHTML = '<div style="color:#666; font-weight:700;">NO TASK</div>';
            }} else {{
                listEl.innerHTML = appUiState.chatTasks.map((task, index) => `
                    <label style="display:flex; align-items:flex-start; gap:10px; padding:8px 6px; border-bottom:1px solid #ececec; cursor:pointer;">
                        <input type="checkbox" data-task-index="${{index}}" style="margin-top:2px; width:16px; height:16px; cursor:pointer;" />
                        <span style="line-height:1.4;">${{headerEscapeHtml(task?.text || '')}}</span>
                    </label>
                `).join('');

                listEl.querySelectorAll('input[type="checkbox"][data-task-index]').forEach((checkbox) => {{
                    checkbox.addEventListener('change', async (event) => {{
                        if (!event.target.checked) return;
                        const idx = Number(event.target.getAttribute('data-task-index'));
                        await completeChatTaskAt(idx);
                    }});
                }});
            }}

            if (!Array.isArray(appUiState.completedTasks) || appUiState.completedTasks.length === 0) {{
                completedEl.innerHTML = '<div style="color:#666;">NO COMPLETED TASKS</div>';
            }} else {{
                completedEl.innerHTML = appUiState.completedTasks.map((task) => `
                    <div style="padding:8px 6px; border-bottom:1px solid #ececec; color:#444;">${{headerEscapeHtml(task?.text || '')}}</div>
                `).join('');
            }}
        }}

        function renderChatUserList() {{
            const wrap = document.getElementById('chatUserList');
            if (!wrap) return;

            const currentUserId = String(appUiState.currentUser?.id || '');
            const orderedUsers = Array.isArray(appUiState.users)
                ? appUiState.users.filter((u) => String(u?.id || '') !== currentUserId)
                : [];
            orderedUsers.sort((a, b) => {{
                const aid = String(a?.id || '');
                const bid = String(b?.id || '');
                const aUnread = appUiState.chatUnreadUserIds.includes(aid);
                const bUnread = appUiState.chatUnreadUserIds.includes(bid);
                if (aUnread && !bUnread) return -1;
                if (!aUnread && bUnread) return 1;
                const aTs = Number(appUiState.chatLastActivityByUser[aid] || 0);
                const bTs = Number(appUiState.chatLastActivityByUser[bid] || 0);
                return bTs - aTs;
            }});

            if (!orderedUsers.length) {{
                wrap.innerHTML = '<div style="padding:10px 8px; color:#666;">No users found.</div>';
                return;
            }}

            wrap.innerHTML = orderedUsers.map((u) => {{
                const id = String(u?.id || '');
                const first = String(u?.first_name || '').trim();
                const last = String(u?.last_name || '').trim();
                const label = `${{first}} ${{last}}`.trim() || String(u?.email || 'Unknown');
                const initials = `${{(first[0] || '').toUpperCase()}}${{(last[0] || '').toUpperCase()}}` || 'U';
                const unread = appUiState.chatUnreadUserIds.includes(id);
                const active = appUiState.chatSelectedUserId && appUiState.chatSelectedUserId === id;
                return `<button type="button" class="chat-user-row${{active ? ' active' : ''}}${{unread ? ' unread' : ''}}" data-chat-user-id="${{headerEscapeHtml(id)}}"><span class="chat-user-avatar">${{headerEscapeHtml(initials)}}</span><span class="chat-user-label">${{headerEscapeHtml(label)}}</span></button>`;
            }}).join('');

            wrap.querySelectorAll('[data-chat-user-id]').forEach((btn) => {{
                btn.addEventListener('click', async () => {{
                    const id = String(btn.getAttribute('data-chat-user-id') || '');
                    appUiState.chatSelectedUserId = id;

                    const hiddenSelect = document.getElementById('chatUserSelect');
                    if (hiddenSelect) hiddenSelect.value = id;

                    await markConversationRead(id);

                    renderChatUserList();
                    renderChatConversation();
                }});
            }});
        }}

        function renderChatConversation() {{
            const titleEl = document.getElementById('chatSelectedUserName');
            const msgsEl = document.getElementById('chatMessagesArea');
            if (!titleEl || !msgsEl) return;

            const selectedId = String(appUiState.chatSelectedUserId || '');
            if (!selectedId) {{
                titleEl.textContent = 'Select a user';
                msgsEl.innerHTML = '<div style="color:#666;">No messages yet.</div>';
                return;
            }}

            const selectedUser = (appUiState.users || []).find((u) => String(u?.id || '') === selectedId);
            const selectedName = `${{String(selectedUser?.first_name || '').trim()}} ${{String(selectedUser?.last_name || '').trim()}}`.trim() || String(selectedUser?.email || 'Selected user');
            titleEl.textContent = selectedName;

            const rows = Array.isArray(appUiState.chatConversations[selectedId]) ? appUiState.chatConversations[selectedId] : [];
            if (!rows.length) {{
                msgsEl.innerHTML = '<div style="color:#666;">No messages yet.</div>';
                return;
            }}

            msgsEl.innerHTML = rows.map((row) => `
                <div class="chat-bubble ${{row.side === 'receiver' ? 'receiver' : 'sender'}}">${{headerEscapeHtml(row.text)}}</div>
            `).join('');
            msgsEl.scrollTop = msgsEl.scrollHeight;
        }}

        async function sendChatPanelMessage() {{
            const selectedId = String(appUiState.chatSelectedUserId || '');
            const textArea = document.getElementById('chatMessageText');
            const messageText = String(textArea?.value || '').trim();
            if (!selectedId) {{
                alert('Select a user first.');
                return;
            }}
            if (!messageText) {{
                alert('Enter a message first.');
                return;
            }}

            await sendHeaderMessage('message');
        }}

        function setActiveMenuItem(screenName) {{
            const items = document.querySelectorAll('.side-menu-item[data-screen]');
            items.forEach((item) => item.classList.toggle('active', item.getAttribute('data-screen') === screenName));
        }}

        function toggleUserDropdown(forceOpen = null) {{
            const menu = document.getElementById('headerUserDropdown');
            if (!menu) return;
            const openNow = menu.style.display === 'block';
            const shouldOpen = forceOpen === null ? !openNow : !!forceOpen;
            menu.style.display = shouldOpen ? 'block' : 'none';
        }}

        async function openChatModal() {{
            const modal = document.getElementById('chatModal');
            if (modal) modal.style.display = 'flex';
            try {{
                await fetchChatMessages();
                deriveChatStateFromMessages();
            }} catch (error) {{
                console.error('Unable to load chat modal data:', error);
            }}
            renderChatTaskPanels();
            renderChatUserList();
            renderChatConversation();

            if (appUiState.chatPollTimer) clearInterval(appUiState.chatPollTimer);
            appUiState.chatPollTimer = setInterval(async () => {{
                const modalEl = document.getElementById('chatModal');
                if (!modalEl || modalEl.style.display !== 'flex') return;
                try {{
                    await fetchChatMessages();
                    deriveChatStateFromMessages();
                    renderChatTaskPanels();
                    renderChatUserList();
                    renderChatConversation();
                }} catch (error) {{
                    console.error('Chat refresh failed:', error);
                }}
            }}, 4000);
        }}

        function closeChatModal() {{
            const modal = document.getElementById('chatModal');
            if (modal) modal.style.display = 'none';
            if (appUiState.chatPollTimer) {{
                clearInterval(appUiState.chatPollTimer);
                appUiState.chatPollTimer = null;
            }}
        }}

        function openProfileModal() {{
            toggleUserDropdown(false);
            const modal = document.getElementById('profileModal');
            if (modal) modal.style.display = 'flex';
        }}

        function closeProfileModal() {{
            const modal = document.getElementById('profileModal');
            if (modal) modal.style.display = 'none';
        }}

        async function sendHeaderMessage(kind) {{
            const select = document.getElementById('chatUserSelect');
            const textArea = document.getElementById('chatMessageText');
            const statusEl = document.getElementById('chatSendStatus');
            const selectedId = String(appUiState.chatSelectedUserId || select?.value || '');
            const userLabel = select ? select.options[select.selectedIndex]?.text || 'Selected user' : 'Selected user';
            const text = String(textArea?.value || '').trim();
            if (!selectedId) {{
                alert('Select a user first.');
                return;
            }}
            if (!text) {{
                alert('Enter a message first.');
                return;
            }}

            try {{
                const response = await fetch('/api/chat/send', {{
                    method: 'POST',
                    credentials: 'include',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        to_user_id: Number(selectedId),
                        kind: kind === 'task' ? 'task' : 'message',
                        text,
                    }}),
                }});
                const data = await response.json();
                if (!response.ok || data.error) throw new Error(data.error || 'Unable to send');

                await fetchChatMessages();
                deriveChatStateFromMessages();
                renderChatTaskPanels();
                renderChatUserList();
                renderChatConversation();

                if (statusEl) statusEl.textContent = kind === 'task'
                    ? `Task added for ${{userLabel}}.`
                    : `Message sent to ${{userLabel}}.`;
            }} catch (error) {{
                alert(String(error.message || 'Unable to send'));
                return;
            }}

            if (select) select.disabled = false;
            if (textArea) {{
                textArea.disabled = false;
                textArea.readOnly = false;
                textArea.value = '';
                textArea.focus();
            }}
        }}

        async function resetProfilePassword() {{
            if (!appUiState.currentUser || !appUiState.currentUser.id) {{
                alert('Current user not available.');
                return;
            }}
            const newPassword = window.prompt('Enter new password:');
            if (!newPassword) return;
            try {{
                const payload = {{ user_ids: [appUiState.currentUser.id], new_password: newPassword }};
                if (appUiState.shopDomain) payload.shop_domain = appUiState.shopDomain;
                const resp = await fetch('/api/setup/users/reset-password', {{
                    method: 'POST',
                    credentials: 'include',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload),
                }});
                const data = await resp.json();
                if (!resp.ok || data.error) throw new Error(data.error || 'Unable to reset password');
                alert('Password reset complete.');
            }} catch (error) {{
                alert(String(error.message || 'Unable to reset password'));
            }}
        }}

        async function initHeaderData() {{
            try {{
                const [sessionResp, contextResp] = await Promise.all([
                    fetch('/api/auth/session', {{ credentials: 'include' }}),
                    fetch('/api/setup/context', {{ credentials: 'include' }}),
                ]);
                const sessionData = await sessionResp.json();
                const contextData = await contextResp.json();
                if (!sessionResp.ok || !sessionData.authenticated) return;
                appUiState.sessionUser = sessionData.user || null;
                appUiState.shopDomain = String(contextData.default_domain || sessionData.user?.domain || '').trim();

                const shopScopeQuery = appUiState.shopDomain
                    ? `?shop_domain=${{encodeURIComponent(appUiState.shopDomain)}}`
                    : '';
                const shopResp = await fetch('/api/setup/shop' + shopScopeQuery, {{ credentials: 'include' }});
                const shopData = await shopResp.json();
                appUiState.shopName = String(shopData?.shop?.shop_name || '').trim();

                const userResp = await fetch(`/api/setup/users${{appUiState.shopDomain ? `?shop_domain=${{encodeURIComponent(appUiState.shopDomain)}}` : ''}}`, {{ credentials: 'include' }});
                const userData = await userResp.json();
                appUiState.users = Array.isArray(userData.users) ? userData.users : [];

                const sessionEmail = String(appUiState.sessionUser?.email || '').toLowerCase();
                appUiState.currentUser = appUiState.users.find((u) => String(u.email || '').toLowerCase() === sessionEmail) || null;

                await fetchChatMessages();
                deriveChatStateFromMessages();

                const firstName = String(appUiState.currentUser?.first_name || '').trim();
                const lastName = String(appUiState.currentUser?.last_name || '').trim();
                const initials = `${{(firstName[0] || '').toUpperCase()}}${{(lastName[0] || '').toUpperCase()}}` || 'U';
                const role = String(appUiState.currentUser?.role || appUiState.sessionUser?.access_level || '-');
                const email = String(appUiState.currentUser?.email || appUiState.sessionUser?.email || '-');

                const bubble = document.getElementById('headerUserButton');
                if (bubble) bubble.textContent = initials;

                const shopText = document.getElementById('profileShopText');
                const roleText = document.getElementById('profileRoleText');
                const emailText = document.getElementById('profileEmailText');
                if (shopText) shopText.textContent = appUiState.shopName || appUiState.shopDomain || '-';
                if (roleText) roleText.textContent = role;
                if (emailText) emailText.textContent = email;

                const currentUserId = String(appUiState.currentUser?.id || '');
                const chatUsers = appUiState.users.filter((u) => String(u?.id || '') !== currentUserId);

                const userSelect = document.getElementById('chatUserSelect');
                if (userSelect) {{
                    userSelect.innerHTML = chatUsers.map((u) => `
                        <option value="${{String(u.id || '')}}">${{String(u.first_name || '').trim()}} ${{String(u.last_name || '').trim()}} (${{String(u.role || '')}})</option>
                    `).join('') || '<option value="">No users found</option>';
                }}

                if (!chatUsers.some((u) => String(u?.id || '') === String(appUiState.chatSelectedUserId || ''))) {{
                    appUiState.chatSelectedUserId = chatUsers.length ? String(chatUsers[0]?.id || '') : '';
                }}
                renderChatUserList();
                renderChatConversation();
                renderChatTaskPanels();
            }} catch (error) {{
                console.error('Header init error:', error);
            }}
        }}

        function initGlobalHeaderUi() {{
            const sidebar = document.getElementById('sideNavSidebar');
            const userButton = document.getElementById('headerUserButton');
            let sidebarSuppressed = false;

            if (sidebar) {{
                sidebar.addEventListener('mouseenter', () => {{
                    if (sidebarSuppressed) return;
                    sidebar.classList.add('expanded');
                }});
                sidebar.addEventListener('mouseleave', () => {{
                    sidebar.classList.remove('expanded');
                    sidebarSuppressed = false;
                }});
            }}
            if (userButton) userButton.addEventListener('click', () => toggleUserDropdown());

            document.querySelectorAll('.side-menu-item[data-screen]').forEach((item) => {{
                item.addEventListener('click', () => {{
                    const target = item.getAttribute('data-screen');
                    switchScreen(target, item);
                    if (sidebar) sidebar.classList.remove('expanded');
                    sidebarSuppressed = true;
                }});
            }});

            document.querySelectorAll('.side-menu-item[data-action="chat"]').forEach((item) => {{
                item.addEventListener('click', async () => {{
                    if (sidebar) sidebar.classList.remove('expanded');
                    sidebarSuppressed = true;
                    await openChatModal();
                }});
            }});

            [document.getElementById('chatModal'), document.getElementById('profileModal')].forEach((modal) => {{
                if (!modal) return;
                modal.addEventListener('click', (event) => {{
                    if (event.target !== modal) return;
                    if (modal.id === 'chatModal') closeChatModal();
                    else modal.style.display = 'none';
                }});
            }});

            document.addEventListener('click', (event) => {{
                const userWrap = document.getElementById('headerUserButton')?.parentElement;
                if (userWrap && !userWrap.contains(event.target)) toggleUserDropdown(false);
            }});
        }}

        function switchScreen(screenName, sourceEl = null) {{
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));

            const nextScreen = document.getElementById(screenName);
            if (!nextScreen) return;
            nextScreen.classList.add('active');
            appUiState.activeScreen = screenName;
            setActiveMenuItem(screenName);

            // Load dashboard data if switching to dashboard
            if (screenName === 'dashboard' && typeof loadDashboardDataIfNeeded === 'function') {{
                loadDashboardDataIfNeeded();
            }}

            if (screenName === 'upload' && typeof loadUploadScreen === 'function') {{
                loadUploadScreen();
            }}

            if (screenName === 'parts' && typeof partsLoadRos === 'function') {{
                partsLoadRos();
                partsLoadVendors();
            }}

            if (screenName === 'tech' && typeof loadTechsList === 'function') {{
                loadTechsList();
            }}

            if (screenName === 'phase' && typeof loadPhaseData === 'function') {{
                loadPhaseData();
            }}

            if (screenName === 'flagtech' && typeof loadFlagoutTechs === 'function') {{
                loadFlagoutTechs();
            }}

            if (screenName === 'reports' && typeof loadReportsData === 'function') {{
                loadReportsData();
            }}

            if (screenName === 'records' && typeof loadRecordsData === 'function') {{
                loadRecordsData();
            }}

            if (screenName === 'setup' && typeof setupLoadData === 'function') {{
                setupLoadData();
            }}
        }}

        initGlobalHeaderUi();
        initHeaderData();
        setActiveMenuItem('dashboard');

        async function logoutApp() {{
            try {{
                await fetch('/api/auth/logout', {{
                    method: 'POST',
                    credentials: 'include',
                }});
            }} catch (e) {{
                console.error('Logout error:', e);
            }} finally {{
                window.location.href = '/ui/login';
            }}
        }}
        
        {get_upload_script()}
        {get_parts_script()}
        {get_setup_script()}
    </script>
</body>
</html>
"""


# ---------------------------------------------------------
# Individual Screen Endpoints
# ---------------------------------------------------------
