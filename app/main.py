from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.estimate import router as estimate_router
from app.routes.ui import router as ui_router  # <-- this line adds the UI

app = FastAPI(title="FlagTech Estimate Parser")

# Configure CORS to allow Wix embed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Wix domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoints
app.include_router(estimate_router, prefix="/api")

# Temporary UI endpoints
app.include_router(ui_router, prefix="/ui")

# Redirect root to UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")