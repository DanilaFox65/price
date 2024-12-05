from pydantic import BaseModel
from typing import List, Optional


class ProductCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryOut(ProductCategoryBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True


class ProductCategoriesList(BaseModel):
    categories: List[ProductCategoryOut]