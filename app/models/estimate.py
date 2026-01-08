from pydantic import BaseModel
from typing import Optional, List

class LineItem(BaseModel):
    line: int
    operation: Optional[str]
    description: str
    part_number: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    labor: Optional[float]
    paint: Optional[float]

class EstimateResponse(BaseModel):
    line_items: List[LineItem]