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
        #appMenuButton svg {{
            display: block;
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
        #sideNavBackdrop {{
            position: fixed;
            left: 0;
            right: 0;
            top: 60px;
            bottom: 0;
            background: rgba(0,0,0,0.3);
            display: none;
            z-index: 1300;
        }}
        #sideNavDrawer {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 260px;
            height: calc(100vh - 60px);
            background: #f2f0ef;
            box-shadow: 2px 0 18px rgba(0,0,0,0.2);
            transform: translateX(-100%);
            transition: transform 0.22s ease;
            z-index: 1310;
            padding: 14px 14px 14px 14px;
            overflow-y: auto;
        }}
        #sideNavDrawer.open {{
            transform: translateX(0);
        }}
        .side-menu-list {{
            display: grid;
            gap: 0;
        }}
        .side-menu-item {{
            width: 100%;
            border: none;
            border-bottom: 1px solid #d0c8c4;
            background: transparent;
            color: #1f1f1f;
            border-radius: 0;
            padding: 14px 12px;
            text-align: center;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 0.6px;
            cursor: pointer;
        }}
        .side-menu-item.active {{
            background: transparent;
            color: #000;
            text-decoration: underline;
            text-underline-offset: 5px;
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
        @media (max-width: 840px) {{
            .content-area {{ padding: 18px; }}
            .app-brand-text {{ font-size: 18px; }}
            .header-chat-layout {{ grid-template-columns: 1fr; }}
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
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
        .phase-cards,
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
    </style>
</head>
<body>
    <header class="app-header">
        <div class="app-header-left">
            <button id="appMenuButton" class="header-icon-btn" type="button" aria-label="Open menu">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M4 7H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M4 12H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M4 17H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
            <img class="app-brand-logo" src="/static/autobodyos.png" alt="AutobodyOS logo" />
            <div class="app-brand-text">AutobodyOS</div>
        </div>
        <div class="app-header-right">
            <button id="headerChatButton" class="header-icon-btn" type="button" aria-label="Open chat">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 5h16v10H8l-4 4V5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
            </button>
            <div style="position:relative;">
                <button id="headerUserButton" type="button" aria-label="Open user menu">--</button>
                <div id="headerUserDropdown">
                    <button type="button" class="header-menu-action" onclick="openProfileModal()">Profile</button>
                    <button type="button" class="header-menu-action" onclick="logoutApp()">Log Out</button>
                </div>
            </div>
        </div>
    </header>

    <div id="sideNavBackdrop"></div>
    <aside id="sideNavDrawer" aria-hidden="true">
        <div class="side-menu-list">
            <button type="button" class="side-menu-item active" data-screen="dashboard">Dashboard</button>
            <button type="button" class="side-menu-item" data-screen="upload">Upload</button>
            <button type="button" class="side-menu-item" data-screen="phase">Roadmap</button>
            <button type="button" class="side-menu-item" data-screen="parts">Parts</button>
            <button type="button" class="side-menu-item" data-screen="tech">Techs</button>
            <button type="button" class="side-menu-item" data-screen="flagtech">Flagout</button>
            <button type="button" class="side-menu-item" data-screen="reports">Reports</button>
            <button type="button" class="side-menu-item" data-screen="setup">Setup</button>
        </div>
    </aside>

    <div id="chatModal" class="header-modal-shell">
        <div class="header-modal-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#333;">Messages & Tasks</h3>
                <button type="button" class="header-menu-action" style="width:auto;" onclick="closeChatModal()">Close</button>
            </div>
            <div class="header-chat-layout">
                <div style="border:1px solid #ddd; border-radius:10px; padding:12px; background:#fafafa;">
                    <div style="font-weight:700; margin-bottom:8px;">Task List</div>
                    <ul style="padding-left:18px; line-height:1.7; color:#333;">
                        <li>Review open repair orders</li>
                        <li>Check pending parts</li>
                        <li>Follow up on flagged tech items</li>
                    </ul>
                </div>
                <div style="border:1px solid #ddd; border-radius:10px; padding:12px; background:#fafafa;">
                    <label for="chatUserSelect" style="display:block; font-weight:700; margin-bottom:6px;">User</label>
                    <select id="chatUserSelect" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:10px;"></select>
                    <textarea id="chatMessageText" rows="4" placeholder="Write a message or task..." style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; resize:vertical;"></textarea>
                    <div style="display:flex; gap:8px; margin-top:10px;">
                        <button type="button" class="header-menu-action" style="width:auto; background:#b22222; color:#fff;" onclick="sendHeaderMessage('message')">Send Message</button>
                        <button type="button" class="header-menu-action" style="width:auto; background:#1f2326; color:#fff;" onclick="sendHeaderMessage('task')">Send Task</button>
                    </div>
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
            users: [],
            currentUser: null,
        }};

        function setActiveMenuItem(screenName) {{
            const items = document.querySelectorAll('.side-menu-item[data-screen]');
            items.forEach((item) => item.classList.toggle('active', item.getAttribute('data-screen') === screenName));
        }}

        function openSideMenu() {{
            const drawer = document.getElementById('sideNavDrawer');
            const backdrop = document.getElementById('sideNavBackdrop');
            if (drawer) drawer.classList.add('open');
            if (backdrop) backdrop.style.display = 'block';
        }}

        function closeSideMenu() {{
            const drawer = document.getElementById('sideNavDrawer');
            const backdrop = document.getElementById('sideNavBackdrop');
            if (drawer) drawer.classList.remove('open');
            if (backdrop) backdrop.style.display = 'none';
        }}

        function toggleUserDropdown(forceOpen = null) {{
            const menu = document.getElementById('headerUserDropdown');
            if (!menu) return;
            const openNow = menu.style.display === 'block';
            const shouldOpen = forceOpen === null ? !openNow : !!forceOpen;
            menu.style.display = shouldOpen ? 'block' : 'none';
        }}

        function openChatModal() {{
            const modal = document.getElementById('chatModal');
            if (modal) modal.style.display = 'flex';
        }}

        function closeChatModal() {{
            const modal = document.getElementById('chatModal');
            if (modal) modal.style.display = 'none';
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

        function sendHeaderMessage(kind) {{
            const select = document.getElementById('chatUserSelect');
            const textArea = document.getElementById('chatMessageText');
            const userLabel = select ? select.options[select.selectedIndex]?.text || 'Selected user' : 'Selected user';
            const text = String(textArea?.value || '').trim();
            if (!text) {{
                alert('Enter a message first.');
                return;
            }}
            alert(`Sent ${{kind}} to ${{userLabel}}.`);
            if (textArea) textArea.value = '';
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

                const userResp = await fetch(`/api/setup/users${{appUiState.shopDomain ? `?shop_domain=${{encodeURIComponent(appUiState.shopDomain)}}` : ''}}`, {{ credentials: 'include' }});
                const userData = await userResp.json();
                appUiState.users = Array.isArray(userData.users) ? userData.users : [];

                const sessionEmail = String(appUiState.sessionUser?.email || '').toLowerCase();
                appUiState.currentUser = appUiState.users.find((u) => String(u.email || '').toLowerCase() === sessionEmail) || null;

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
                if (shopText) shopText.textContent = appUiState.shopDomain || '-';
                if (roleText) roleText.textContent = role;
                if (emailText) emailText.textContent = email;

                const userSelect = document.getElementById('chatUserSelect');
                if (userSelect) {{
                    userSelect.innerHTML = appUiState.users.map((u) => `
                        <option value="${{String(u.id || '')}}">${{String(u.first_name || '').trim()}} ${{String(u.last_name || '').trim()}} (${{String(u.role || '')}})</option>
                    `).join('') || '<option value="">No users found</option>';
                }}
            }} catch (error) {{
                console.error('Header init error:', error);
            }}
        }}

        function initGlobalHeaderUi() {{
            const menuButton = document.getElementById('appMenuButton');
            const menuBackdrop = document.getElementById('sideNavBackdrop');
            const drawer = document.getElementById('sideNavDrawer');
            const chatButton = document.getElementById('headerChatButton');
            const userButton = document.getElementById('headerUserButton');

            if (menuButton) menuButton.addEventListener('click', openSideMenu);
            if (menuBackdrop) menuBackdrop.addEventListener('click', closeSideMenu);
            if (chatButton) chatButton.addEventListener('click', openChatModal);
            if (userButton) userButton.addEventListener('click', () => toggleUserDropdown());

            document.querySelectorAll('.side-menu-item[data-screen]').forEach((item) => {{
                item.addEventListener('click', () => {{
                    const target = item.getAttribute('data-screen');
                    switchScreen(target, item);
                    closeSideMenu();
                }});
            }});

            [document.getElementById('chatModal'), document.getElementById('profileModal')].forEach((modal) => {{
                if (!modal) return;
                modal.addEventListener('click', (event) => {{
                    if (event.target === modal) modal.style.display = 'none';
                }});
            }});

            document.addEventListener('click', (event) => {{
                if (drawer && drawer.contains(event.target)) return;
                if (menuButton && menuButton.contains(event.target)) return;
                if (menuBackdrop && menuBackdrop.style.display === 'block' && !drawer?.classList.contains('open')) {{
                    menuBackdrop.style.display = 'none';
                }}

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
