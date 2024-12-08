from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ShopCreate(BaseModel):
    name: str  # Название магазина
    description: Optional[str] = None  # Описание магазина (необязательно)
    address: str  # Адрес магазина

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy

class ShopUpdate(BaseModel):
    name: Optional[str] = None  # Название магазина (опционально для обновления)
    description: Optional[str] = None  # Описание магазина (опционально для обновления)
    address: Optional[str] = None  # Адрес магазина (опционально для обновления)

    class Config:
        orm_mode = True  # Параметр для использования моделей SQLAlchemy