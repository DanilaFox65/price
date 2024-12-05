from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int

    class Config:
        orm_mode = True


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category_id: int

    class Config:
        orm_mode = True