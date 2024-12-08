from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Shop
from src.dependencies.authentication import get_db
from src.shop.schemas import ShopCreate, ShopUpdate  # Импортируем схему для создания магазина
from datetime import datetime

router = APIRouter()

@router.post(
    "/shop/create",
    description="Создание нового магазина",
    summary="Создание нового магазина",
    responses={
        200: {"description": "Магазин успешно создан"},
        400: {"description": "Ошибка валидации данных"},
    }
)
async def create_shop(
    shop: ShopCreate,
    db_connect: AsyncSession = Depends(get_db)
):
    # Проверка, если магазин с таким названием уже существует
    existing_shop = await db_connect.execute(
        select(Shop).filter(Shop.name == shop.name)
    )
    if existing_shop.scalars().first():
        raise HTTPException(status_code=400, detail="Магазин с таким названием уже существует")

    # Создание нового магазина
    new_shop = Shop(
        name=shop.name,
        description=shop.description,
        address=shop.address,
    )

    # Добавление магазина в базу данных
    db_connect.add(new_shop)
    await db_connect.commit()
    await db_connect.refresh(new_shop)

    return {
        "id": new_shop.id,
        "name": new_shop.name,
        "description": new_shop.description,
        "address": new_shop.address,
        "created_at": new_shop.created_at,
        "updated_at": new_shop.updated_at,
    }

@router.put(
    "/shop/{shop_id}",
    description="Обновление данных магазина по id",
    summary="Обновление данных магазина по id",
    responses={
        200: {"description": "Магазин успешно обновлен"},
        404: {"description": "Магазин не найден"},
    }
)
async def update_shop(
    shop_id: int,
    shop_update: ShopUpdate,  # Схема для обновления
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем магазин по ID
    shop = await db_connect.execute(
        select(Shop).filter(Shop.id == shop_id)
    )
    shop = shop.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Магазин не найден")

    # Обновляем поля магазина на основе данных из запроса
    if shop_update.name is not None:
        shop.name = shop_update.name
    if shop_update.description is not None:
        shop.description = shop_update.description
    if shop_update.address is not None:
        shop.address = shop_update.address

    # Сохраняем изменения в базе данных
    db_connect.add(shop)
    await db_connect.commit()
    await db_connect.refresh(shop)

    return {
        "id": shop.id,
        "name": shop.name,
        "description": shop.description,
        "address": shop.address,
        "created_at": shop.created_at,
        "updated_at": shop.updated_at,
    }

@router.delete(
    "/shop/{shop_id}",
    description="Мягкое удаление магазина по id",
    summary="Мягкое удаление магазина по id",
    responses={
        200: {"description": "Магазин успешно удален"},
        404: {"description": "Магазин не найден"},
        400: {"description": "Магазин уже удален"},
    }
)
async def soft_delete_shop(
    shop_id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем магазин по ID
    shop = await db_connect.execute(
        select(Shop).filter(Shop.id == shop_id)
    )
    shop = shop.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Магазин не найден")

    # Проверяем, был ли уже удалён магазин
    if shop.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Магазин уже удален")

    # Мягкое удаление (обновляем поле deleted_at)
    shop.deleted_at = datetime.utcnow()

    # Сохраняем изменения в базе данных
    db_connect.add(shop)
    await db_connect.commit()
    await db_connect.refresh(shop)

    return {"message": "Магазин успешно удален"}


@router.get(
    "/shop/{shop_id}",
    description="Получение магазина по id",
    summary="Получение магазина по id",
    responses={
        200: {"description": "Магазин найден", "content": {"application/json": {"example": {"id": 1, "name": "Shop 1", "description": "Description", "address": "Address"}}}},
        404: {"description": "Магазин не найден"},
    }
)
async def get_shop_by_id(
    shop_id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем магазин по ID
    shop = await db_connect.execute(
        select(Shop).filter(Shop.id == shop_id)
    )
    shop = shop.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Магазин не найден")

    # Возвращаем данные о магазине
    return {
        "id": shop.id,
        "name": shop.name,
        "description": shop.description,
        "address": shop.address,
        "created_at": shop.created_at,
        "updated_at": shop.updated_at,
        "deleted_at": shop.deleted_at,
    }
