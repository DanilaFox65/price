from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str  # Название продукта
    description: Optional[str] = None  # Описание продукта (необязательно)
    category_id: int  # ID категории, к которой относится продукт

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy

class ProductOut(BaseModel):
    id: int  # Идентификатор продукта
    name: str  # Название продукта
    description: Optional[str] = None  # Описание продукта
    category_id: int  # ID категории продукта
    created_at: datetime  # Дата создания продукта
    updated_at: datetime  # Дата последнего обновления продукта

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        orm_mode = True

