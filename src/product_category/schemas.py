from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Схема для создания категории товара
class ProductCategoryCreate(BaseModel):
    name: str  # Название категории
    description: Optional[str] = None  # Описание категории (необязательно)

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy

# Схема для вывода информации о категории товара
class ProductCategoryOut(BaseModel):
    id: int  # Идентификатор категории
    name: str  # Название категории
    description: Optional[str] = None  # Описание категории (необязательно)
    created_at: str  # Дата создания категории (в формате ISO 8601)
    updated_at: str  # Дата последнего обновления категории (в формате ISO 8601)
    deleted_at: Optional[str] = None

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy

# Схема для вывода информации о продукте
class ProductOut(BaseModel):
    id: int  # Идентификатор продукта
    name: str  # Название продукта
    description: Optional[str] = None  # Описание продукта (необязательно)
    category_id: int  # Идентификатор категории продукта
    created_at: datetime  # Дата создания продукта
    updated_at: datetime  # Дата последнего обновления продукта
    deleted_at: Optional[datetime] = None  # Дата мягкого удаления продукта (если применимо)

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy