"""Estimator page. The Estimates screen opens this instead of the old unsaved popup."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_PAGE = Path(__file__).resolve().parents[2] / "templates" / "native_estimate.html"


@router.get("/native-estimate", response_class=HTMLResponse)
async def native_estimate_page():
    return HTMLResponse(_PAGE.read_text(encoding="utf-8"))
