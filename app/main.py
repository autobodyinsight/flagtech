from fastapi import FastAPI
from app.routes.estimate import router as estimate_router

app = FastAPI(title="FlagTech Estimate Parser")

app.include_router(estimate_router, prefix="/api")