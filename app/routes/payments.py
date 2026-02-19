from fastapi import APIRouter, Request, HTTPException
from app.services.db import close_repair_order

router = APIRouter()

@router.post("/api/payments/close-ro")
async def close_ro(request: Request):
    data = await request.json()
    ro_number = data.get("ro")
    if not ro_number:
        raise HTTPException(status_code=400, detail="Missing RO number")
    try:
        close_repair_order(ro_number)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
