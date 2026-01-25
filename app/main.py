from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routes.estimate import router as estimate_router
from app.routes.UI.ui import router as ui_router
from app.routes.UI.ui_with_processing import router as processing_router

# ⭐ NEW: import your save‑routes router
from app.routes.UI.upload_ui.routes import router as ui_routes_router

app = FastAPI(title="FlagTech Estimate Parser")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autobodyinsight.github.io",
        "https://autobodyinsight.github.io/flagtech",
        "https://www.autobodyinsight.github.io",
        "https://www.autobodyinsight.github.io/flagtech",
        # Add your Wix domain after publishing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoints
app.include_router(estimate_router, prefix="/api")

# Main UI display
app.include_router(ui_router, prefix="/ui")

# PDF processing routes
app.include_router(processing_router, prefix="/ui")

# ⭐ NEW: Save routes (labor + refinish)
app.include_router(ui_routes_router, prefix="/ui")

# Redirect root to UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")