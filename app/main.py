from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Routers
from app.routes.estimate import router as estimate_router
from app.routes.users import router as users_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router
from app.routes.UI.upload_ui.routes import router as ui_routes_router
from app.routes.auth import router as auth_router
from app.routes.payments import router as payments_router
from app.services.auth import SESSION_COOKIE_NAME, get_session_by_token


app = FastAPI(title="FlagTech Estimate Parser")


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DISABLE_LOGIN_SCREEN = _env_flag("FLAGTECH_DISABLE_LOGIN_SCREEN", True)

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
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    public_prefixes = (
        "/auth",
        "/docs",
        "/redoc",
        "/openapi.json",
    )
    if request.method == "OPTIONS" or any(path.startswith(prefix) for prefix in public_prefixes):
        return await call_next(request)

    protected_path = path == "/" or path.startswith("/ui") or path.startswith("/api")
    if not protected_path:
        return await call_next(request)

    token = request.cookies.get(SESSION_COOKIE_NAME)
    session = get_session_by_token(token) if token else None
    if not session:
        if DISABLE_LOGIN_SCREEN:
            request.state.user = {
                "email": "guest@flagtech.local",
                "domain": "default",
                "company_name": "Default Shop",
                "access_level": "architect",
            }
            return await call_next(request)

        if path.startswith("/api"):
            return JSONResponse({"detail": "Authentication required"}, status_code=401)
        return RedirectResponse(url="/auth/login?reason=auth_required", status_code=303)

    request.state.user = session
    return await call_next(request)

# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

# API endpoints
app.include_router(estimate_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(payments_router, prefix="/api")

# Authentication endpoints
app.include_router(auth_router)

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
    return RedirectResponse(url="/ui/")