from fastapi import APIRouter, Request, HTTPException
from app.services.db import close_repair_order
from app.services.middleware import get_user_domain

router = APIRouter()

@router.post("/api/payments/close-ro")
async def close_ro(request: Request):
    if not get_user_domain(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    raise HTTPException(status_code=410, detail="Deprecated endpoint. Use /api/payments/close-ro from main estimate routes.")
