from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Product, ProductCategory
from src.dependencies.authentication import get_db
from src.product.schemas import ProductCreate, ProductOut, ProductUpdate
from datetime import datetime

router = APIRouter()

@router.post(
    "/product/create",
    response_model=ProductOut,
    description="Создание нового продукта",
    summary="Создание нового продукта",
    responses={
        200: {"description": "Продукт успешно создан"},
        400: {"description": "Ошибка валидации данных"},
        404: {"description": "Категория не найдена"},
    }
)
async def create_product(
    product: ProductCreate,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductOut:
    # Проверка на существование категории с таким id
    existing_category = (await db_connect.execute(
        select(ProductCategory).filter(ProductCategory.id == product.category_id)
    )).scalar_one_or_none()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Создание нового продукта
    new_product = Product(
        name=product.name,
        description=product.description,
        category_id=product.category_id,

    )

    # Добавление в базу данных
    db_connect.add(new_product)
    await db_connect.commit()
    await db_connect.refresh(new_product)

    return ProductOut(
        id=new_product.id,
        name=new_product.name,
        description=new_product.description,
        category_id=new_product.category_id,
        created_at=new_product.created_at,
        updated_at=new_product.updated_at
    )

@router.put(
    "/product/{product_id}",
    response_model=ProductOut,
    description="Обновление данных продукта",
    summary="Обновление данных продукта",
    responses={
        200: {"description": "Продукт успешно обновлён"},
        404: {"description": "Продукт не найден"},
    }
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductOut:
    # Ищем продукт по ID
    existing_product = (await db_connect.execute(
        select(Product).filter(Product.id == product_id)
    )).scalar_one_or_none()

    if not existing_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Обновляем все поля, переданные в запросе
    if product_update.name is not None:
        existing_product.name = product_update.name
    if product_update.description is not None:
        existing_product.description = product_update.description
    if product_update.category_id is not None:
        existing_product.category_id = product_update.category_id

    # Сохраняем изменения в базе данных
    db_connect.add(existing_product)
    await db_connect.commit()
    await db_connect.refresh(existing_product)

    return ProductOut(
        id=existing_product.id,
        name=existing_product.name,
        description=existing_product.description,
        category_id=existing_product.category_id,
        created_at=existing_product.created_at,
        updated_at=existing_product.updated_at
    )

@router.delete(
    "/product/{product_id}",
    description="Мягкое удаление продукта по id",
    summary="Мягкое удаление продукта по id",
    responses={
        200: {"description": "Продукт успешно удалён"},
        404: {"description": "Продукт не найден"},
        400: {"description": "Продукт уже удалён"},
    }
)
async def soft_delete_product(
    product_id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем продукт по ID
    existing_product = (await db_connect.execute(
        select(Product).filter(Product.id == product_id)
    )).scalar_one_or_none()

    if not existing_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Проверка на уже удалённый продукт
    if existing_product.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Продукт уже удалён")

    # Мягкое удаление (обновляем поле deleted_at)
    existing_product.deleted_at = datetime.utcnow()

    # Сохраняем изменения в базе данных
    db_connect.add(existing_product)
    await db_connect.commit()
    await db_connect.refresh(existing_product)

    return {"message": "Продукт успешно удалён"}

