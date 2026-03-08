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
        .tab-bar {{
            background-color: #3c4142;
            display: flex;
            align-items: center;
            gap: 0;
            padding: 0;
            border-bottom: 3px solid #333;
        }}
        .tab-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-right: 1px solid #555;
            color: #fff;
            flex: 0 0 auto;
            min-width: 210px;
        }}
        .tab-brand-logo {{
            width: 34px;
            height: 34px;
            border-radius: 8px;
            object-fit: contain;
            background: rgba(255, 255, 255, 0.95);
            padding: 3px;
        }}
        .tab-brand-label {{
            font-weight: 700;
            font-size: 18px;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }}
        .nav-tab {{
            padding: 18px 35px;
            background-color: #3c4142;
            color: white;
            opacity: 1;
            background-image: none;
            box-shadow: none;
            filter: none;
            text-align: center;
            cursor: pointer;
            font-weight: bold;
            border-right: 1px solid #555;
            transition: all 0.3s ease;
            font-size: 14px;
            flex: 1;
            max-width: 200px;
        }}
        .nav-tab:hover {{
            background-color: #3c4142;
        }}
        .nav-tab.active {{
            background-color: #b22222;
            color: white;
            border-bottom: 3px solid #b22222;
            margin-bottom: -3px;
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
        button:not([style*="background:none"]):not([style*="background: none"]):not(.link-button):not(.tech-link) {{
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
    <div class="tab-bar">
        <div class="tab-brand">
            <img class="tab-brand-logo" src="/static/autobodyos.png" alt="AutobodyOS logo" />
            <span class="tab-brand-label">AutobodyOS</span>
        </div>
        <div class="nav-tab active" onclick="switchScreen('dashboard')">DASHBOARD</div>
        <div class="nav-tab" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-tab" onclick="switchScreen('parts')">PARTS</div>
        <div class="nav-tab" onclick="switchScreen('tech')">TECHS</div>
        <div class="nav-tab" onclick="switchScreen('phase')">ROADMAP</div>
        <div class="nav-tab" onclick="switchScreen('flagtech')">FLAGOUT</div>
        <div class="nav-tab" onclick="switchScreen('reports')">REPORTS</div>
        <div class="nav-tab" onclick="switchScreen('records')">RECORDS</div>
        <div class="nav-tab" onclick="switchScreen('setup')">SETUP</div>
        <div class="nav-tab" onclick="logoutApp()">LOGOUT</div>
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

        function switchScreen(screenName) {{
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));
            
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(screenName).classList.add('active');
            event.target.classList.add('active');            
            // Load dashboard data if switching to dashboard
            if (screenName === 'dashboard' && typeof loadDashboardDataIfNeeded === 'function') {{
                loadDashboardDataIfNeeded();
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

            if (screenName === 'records' && typeof loadRecordsData === 'function') {{
                loadRecordsData();
            }}

            if (screenName === 'setup' && typeof setupLoadData === 'function') {{
                setupLoadData();
            }}
        }}

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
