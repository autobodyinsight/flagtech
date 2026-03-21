from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.services.schema_bootstrap import initialize_application_schema
from app.services.middleware import validate_request_session

# Routers
from app.routes.estimate import router as estimate_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router
from app.routes.UI.upload_ui.routes import router as ui_routes_router
from app.routes.UI.reports import router as reports_router
from app.routes.payments import router as payments_router



@asynccontextmanager
async def app_lifespan(app: FastAPI):
    initialize_application_schema()
    yield


app = FastAPI(title="FlagTech Estimate Parser", lifespan=app_lifespan)

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


@app.middleware("http")
async def permission_guard_middleware(request, call_next):
    path = str(request.url.path or "").strip()

    if not path or path == "/" or path.startswith("/static/"):
        return await call_next(request)

    if path in {"/ui/login", "/api/auth/login", "/api/auth/logout", "/api/auth/session"}:
        return await call_next(request)

    if not (path.startswith("/ui") or path.startswith("/api")):
        return await call_next(request)

    session_info = validate_request_session(request)
    if not session_info:
        if path.startswith("/ui") and request.method.upper() == "GET":
            return RedirectResponse(url="/ui/login")
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    request.state.user_id = session_info.get("user_id")
    request.state.permission_snapshot = session_info.get("permission_snapshot") or {}

    return await call_next(request)

# ---------------------------------------------------------
# ROOT REDIRECT
# ---------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/login")