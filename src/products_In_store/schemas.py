from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductsInStoreBase(BaseModel):
    """
    Базовая схема для модели ProductsInStore.
    """
    product_id: int
    shop_id: int
    price: int

    class Config:
        orm_mode = True  # Для работы с объектами SQLAlchemy

class ProductsInStoreCreate(ProductsInStoreBase):
    """
    Схема для создания записи ProductsInStore.
    """
    pass

class ProductsInStoreOut(BaseModel):
    """
    Схема для вывода информации о записи ProductsInStore.
    """
    id: int
    product_id: int
    shop_id: int
    price: int

    class Config:
        orm_mode = True  # Для работы с объектами SQLAlchemy

from pydantic import BaseModel, Field

class ProductsInStoreUpdatePrice(BaseModel):
    product_id: int = Field(..., description="ID продукта")
    shop_id: int = Field(..., description="ID магазина")
    price: int = Field(..., gt=0, description="Новая цена продукта (должна быть больше 0)")

    class Config:
        orm_mode = True
