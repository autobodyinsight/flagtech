from fastapi import APIRouter, UploadFile, File
from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse

router = APIRouter()

@router.post("/parse-estimate", response_model=EstimateResponse)
async def parse_estimate(file: UploadFile = File(...)):
    doc = load_pdf(file)
    line_items = parse_estimate_pdf(doc)
    return {"line_items": line_items}