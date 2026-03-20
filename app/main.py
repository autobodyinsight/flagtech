from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Routers
from app.routes.estimate import router as estimate_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router
from app.routes.UI.upload_ui.routes import router as ui_routes_router
from app.routes.UI.reports import router as reports_router
from app.routes.payments import router as payments_router
from app.services.middleware import (
    DEFAULT_SCOPE_DOMAIN,
    get_architect_view_domain,
    get_authenticated_user,
    is_architect_view_mode,
)


app = FastAPI(title="FlagTech Estimate Parser")

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------

# Add every frontend origin that needs access to Render backend
ALLOWED_ORIGINS = [
    # GitHub Pages (public site)
    "https://autobodyinsight.github.io",

    # Wix domain (embedded iframe)
    "https://www.autobodyinsight.com",

    # GitHub Codespaces (your dev environment)
    # IMPORTANT: Codespaces generates a NEW URL every time.
    # Add your current one here:
    "https://studious-space-doodle-jjw4vjxg77w7f5vq-8000.app.github.dev",

    # Local development (optional)
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def architect_view_mode_read_only_guard(request: Request, call_next):
    method = str(request.method or "").upper()
    if method not in {"GET", "HEAD", "OPTIONS"}:
        user = get_authenticated_user(request)
        if user and bool(user.get("is_architect")) and is_architect_view_mode(request):
            scoped_domain = str(get_architect_view_domain(request) or "").strip().lower()
            if scoped_domain == str(DEFAULT_SCOPE_DOMAIN or "").strip().lower():
                return await call_next(request)
            path = str(request.url.path or "")
            allowed_write_paths = {
                "/api/architect/view-mode",
                "/api/auth/logout",
            }
            if path not in allowed_write_paths:
                return JSONResponse(status_code=403, content={"error": "VIEW MODE ONLY"})
    return await call_next(request)

# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

# API endpoints
app.include_router(estimate_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(reports_router)

# Main UI display
app.include_router(ui_router, prefix="/ui")

# PDF processing routes
app.include_router(processing_router, prefix="/ui")

# Save routes (labor + refinish)
app.include_router(ui_routes_router, prefix="/ui")

# ---------------------------------------------------------
# ROOT REDIRECT
# ---------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/login")