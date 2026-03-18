from pydantic import BaseModel
from typing import Optional, List


class User(BaseModel):
    id: int
    email: str
    password: Optional[str] = None
    role: str
    shop_id: int


class Shop(BaseModel):
    id: int
    name: str
    address: str
    city: str
    state: str
    zip: str

class LineItem(BaseModel):
    line: int
    operation: Optional[str]
    description: str
    labor: Optional[float]
    paint: Optional[float]
    

class EstimateResponse(BaseModel):
    line_items: List[LineItem]