from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import os
import time
from app.services.schema_bootstrap import initialize_application_schema
from app.services.middleware import get_authenticated_user, validate_request_session
from app.services.permissions import has_feature_access, resolve_feature_for_path
from app.services.db import get_conn

# Routers
from app.routes.estimate import router as estimate_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router
from app.routes.UI.upload_ui.routes import router as ui_routes_router
from app.routes.UI.reports import router as reports_router
from app.routes.payments import router as payments_router
from app.routes.UI.native_estimate import router as native_estimate_page_router


logger = logging.getLogger("flagtech.request_timing")



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
app.include_router(native_estimate_page_router, prefix="/ui")


@app.middleware("http")
async def permission_guard_middleware(request, call_next):
    path = str(request.url.path or "").strip()

    if not path or path == "/" or path.startswith("/static/"):
        return await call_next(request)

    if path in {
        "/ui/login",
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/session",
        "/api/auth/forgot-password",
        "/api/auth/reset-password",
        "/health",
    }:
        return await call_next(request)

    if not (path.startswith("/ui") or path.startswith("/api")):
        return await call_next(request)

    session_info = validate_request_session(request)
    if not session_info:
        if path.startswith("/ui") and request.method.upper() == "GET":
            return RedirectResponse(url="/ui/login")
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    request.state.user_id = session_info.get("user_id")
    user = get_authenticated_user(request)
    if not user:
        if path.startswith("/ui") and request.method.upper() == "GET":
            return RedirectResponse(url="/ui/login")
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    snapshot = user.get("permissions") or {}
    request.state.permission_snapshot = snapshot
    feature = resolve_feature_for_path(path, request.method)
    if feature and not has_feature_access(snapshot, feature):
        if path.startswith("/ui") and request.method.upper() == "GET":
            return RedirectResponse(url="/ui/")
        return JSONResponse(status_code=403, content={"error": "You do not have access to this feature"})

    origin = str(request.headers.get("origin") or "").strip()
    if origin and request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        host = str(request.headers.get("host") or "")
        allowed = set(ALLOWED_ORIGINS)
        allowed.add(f"https://{host}")
        allowed.add(f"http://{host}")
        if origin not in allowed:
            return JSONResponse(status_code=403, content={"error": "Cross-site request blocked"})

    return await call_next(request)


@app.middleware("http")
async def request_timing_middleware(request, call_next):
    path = str(request.url.path or "")
    if path.startswith("/static/"):
        return await call_next(request)

    method = request.method.upper()
    start_time = time.perf_counter()
    logger.info("req_start method=%s path=%s", method, path)
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception("req_error method=%s path=%s duration_ms=%.1f", method, path, duration_ms)
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "req_done method=%s path=%s status=%s duration_ms=%.1f",
        method,
        path,
        response.status_code,
        duration_ms,
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("X-XSS-Protection", "0")
    response.headers.setdefault("Content-Security-Policy", "frame-ancestors 'self'")
    if os.getenv("FLAGTECH_ENV", "development") == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

# ---------------------------------------------------------
# ROOT REDIRECT
# ---------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/login")


@app.get("/health")
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 AS ok")
            row = cur.fetchone() or {}
        finally:
            cur.close()
        database = "ok" if int(row.get("ok") or 0) == 1 else "error"
    except Exception:
        logger.exception("health_check_failed")
        return JSONResponse(status_code=503, content={"status": "error", "database": "error"})
    return {"status": "ok", "database": database, "environment": os.getenv("FLAGTECH_ENV", "development")}


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    logger.exception("unhandled_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})