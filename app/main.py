from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.routes.estimate import router as estimate_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router
from app.routes.UI.upload_ui.routes import router as ui_routes_router


app = FastAPI(title="FlagTech Estimate Parser")

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