from fastapi import FastAPI
from app.routes.estimate import router as estimate_router
from app.routes.ui import router as ui_router   # <-- add this

app = FastAPI(title="FlagTech Estimate Parser")

# API endpoints
app.include_router(estimate_router, prefix="/api")

# Temporary UI endpoints
app.include_router(ui_router, prefix="/ui")