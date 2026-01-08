from fastapi import APIRouter, UploadFile, File
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.models.estimate import EstimateResponse

router = APIRouter()

@router.post("/parse-estimate", response_model=EstimateResponse)
async def parse_estimate(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    line_items = parse_estimate_text(text)
    return {"line_items": line_items}