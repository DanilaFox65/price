from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ProductsInStore, Product, Shop
from src.dependencies.authentication import get_db
from pydantic import BaseModel
from datetime import datetime

from src.products_In_store.schemas import ProductsInStoreUpdatePrice

router = APIRouter()

class ProductsInStoreCreate(BaseModel):
    product_id: int
    shop_id: int
    price: int

    class Config:
        orm_mode = True

class ProductsInStoreOut(BaseModel):
    id: int
    product_id: int
    shop_id: int
    price: int

    class Config:
        orm_mode = True

@router.post(
    "/products-in-store/create",
    response_model=ProductsInStoreOut,
    description="Добавить продукт в магазин",
    summary="Добавить продукт в магазин",
    responses={
        200: {"description": "Продукт успешно добавлен в магазин"},
        400: {"description": "Ошибка валидации данных"},
        404: {"description": "Продукт или магазин не найден"},
    }
)
async def add_product_to_store(
    entry: ProductsInStoreCreate,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductsInStoreOut:
    # Проверка существования продукта
    product = await db_connect.execute(
        select(Product).filter(Product.id == entry.product_id)
    )
    product = product.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Проверка существования магазина
    shop = await db_connect.execute(
        select(Shop).filter(Shop.id == entry.shop_id)
    )
    shop = shop.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Магазин не найден")

    # Создание записи
    new_entry = ProductsInStore(
        product_id=entry.product_id,
        shop_id=entry.shop_id,
        price=entry.price
    )
    db_connect.add(new_entry)
    await db_connect.commit()
    await db_connect.refresh(new_entry)

    return ProductsInStoreOut(
        id=new_entry.id,
        product_id=new_entry.product_id,
        shop_id=new_entry.shop_id,
        price=new_entry.price
    )

@router.delete(
    "/products-in-store/{id}",
    description="Мягкое удаление продукта из магазина",
    summary="Мягкое удаление продукта из магазина",
    responses={
        200: {"description": "Продукт успешно удален из магазина"},
        404: {"description": "Продукт в магазине не найден"},
    }
)
async def soft_delete_product_from_store(
    id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем запись о товаре в магазине
    entry = await db_connect.execute(
        select(ProductsInStore).filter(ProductsInStore.id == id)
    )
    entry = entry.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Продукт в магазине не найден")

    # Проверяем, не удален ли уже
    if entry.deleted_at:
        raise HTTPException(status_code=400, detail="Запись уже удалена")

    # Мягкое удаление
    entry.deleted_at = datetime.utcnow()
    await db_connect.commit()

    return {"message": "Продукт успешно удален из магазина"}

@router.get(
    "/products-in-store/shop/{shop_id}",
    description="Получение всех товаров в магазине",
    summary="Получение всех товаров в магазине",
    responses={
        200: {"description": "Список товаров получен"},
        404: {"description": "Магазин не найден"},
    }
)
async def get_products_in_store(
    shop_id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Проверяем существование магазина
    shop = await db_connect.execute(
        select(Shop).filter(Shop.id == shop_id)
    )
    shop = shop.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Магазин не найден")

    # Получаем все продукты в магазине
    products = await db_connect.execute(
        select(ProductsInStore).filter(
            ProductsInStore.shop_id == shop_id,
            ProductsInStore.deleted_at.is_(None)
        )
    )
    products = products.scalars().all()

    return [
        {
            "id": product.id,
            "product_id": product.product_id,
            "shop_id": product.shop_id,
            "price": product.price
        } for product in products
    ]
@router.put(
    "/products-in-store/{products_in_store_id}/update-price",
    response_model=ProductsInStoreOut,
    description="Изменение цены продукта по ID записи в таблице ProductsInStore",
    summary="Изменение цены продукта по ID",
    responses={
        200: {"description": "Цена продукта успешно обновлена"},
        404: {"description": "Запись с указанным ID не найдена"},
    }
)
async def update_price_by_id(
    products_in_store_id: int,
    new_price: int,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductsInStoreOut:
    # Поиск записи в таблице ProductsInStore по ID
    entry = await db_connect.execute(
        select(ProductsInStore).filter(ProductsInStore.id == products_in_store_id)
    )
    entry = entry.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись с указанным ID не найдена")

    # Обновление цены
    entry.price = new_price
    await db_connect.commit()
    await db_connect.refresh(entry)

    return ProductsInStoreOut(
        id=entry.id,
        product_id=entry.product_id,
        shop_id=entry.shop_id,
        price=entry.price,
    )

