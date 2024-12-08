from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ProductCategory
from src.dependencies.authentication import get_db
from src.product_category.schemas import ProductCategoryOut, ProductCategoryCreate
from datetime import datetime


router = APIRouter()


@router.post(
    "/category/create",
    response_model=ProductCategoryOut,
    description="Создание новой категории товара",
    summary="Создание новой категории товара",
    responses={
        200: {"description": "Категория успешно создана"},
        400: {"description": "Ошибка валидации данных"},
        409: {"description": "Категория с таким именем уже существует"},
    }
)
async def create_category(
    category: ProductCategoryCreate,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductCategoryOut:
    # Проверка на существование категории с таким именем
    existing_category = (await db_connect.execute(
        select(ProductCategory).filter(ProductCategory.name == category.name)
    )).scalar_one_or_none()

    if existing_category:
        raise HTTPException(status_code=409, detail="Категория с таким именем уже существует")

    # Создание новой категории
    new_category = ProductCategory(
        name=category.name,
        description=category.description
    )

    # Добавление в базу данных
    db_connect.add(new_category)
    await db_connect.commit()
    await db_connect.refresh(new_category)

    return ProductCategoryOut(
        id=new_category.id,
        name=new_category.name,
        description=new_category.description,
        created_at=new_category.created_at.isoformat(),
        updated_at=new_category.updated_at.isoformat()
    )

@router.put(
    "/category/{category_id}",
    response_model=ProductCategoryOut,
    description="Обновление категории товара по id",
    summary="Обновление категории товара по id",
    responses={
        200: {"description": "Категория успешно обновлена"},
        404: {"description": "Категория не найдена"},
        400: {"description": "Ошибка валидации данных"},
    }
)
async def update_category(
    category_id: int,
    category: ProductCategoryCreate,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductCategoryOut:
    # Ищем категорию по ID
    existing_category = (await db_connect.execute(
        select(ProductCategory).filter(ProductCategory.id == category_id)
    )).scalar_one_or_none()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Обновляем поля категории
    if category.name:
        existing_category.name = category.name
    if category.description:
        existing_category.description = category.description

    # Сохраняем изменения в базе данных
    await db_connect.commit()
    await db_connect.refresh(existing_category)

    return ProductCategoryOut(
        id=existing_category.id,
        name=existing_category.name,
        description=existing_category.description,
        created_at=existing_category.created_at.isoformat(),
        updated_at=existing_category.updated_at.isoformat()
    )

@router.delete(
    "/category/{category_id}",
    description="Мягкое удаление категории товара по id",
    summary="Мягкое удаление категории товара по id",
    responses={
        200: {"description": "Категория успешно удалена"},
        404: {"description": "Категория не найдена"},
    }
)
async def soft_delete_category(
    category_id: int,
    db_connect: AsyncSession = Depends(get_db)
):
    # Ищем категорию по ID
    existing_category = (await db_connect.execute(
        select(ProductCategory).filter(ProductCategory.id == category_id)
    )).scalar_one_or_none()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Мягкое удаление (обновляем поле deleted_at)
    if existing_category.deleted_at:
        raise HTTPException(status_code=400, detail="Категория уже удалена")

    existing_category.deleted_at = datetime.utcnow()

    # Сохраняем изменения в базе данных
    await db_connect.commit()
    await db_connect.refresh(existing_category)

    return {"message": "Категория успешно удалена"}

@router.get(
    "/category/{category_id}",
    response_model=ProductCategoryOut,
    description="Получение информации о категории товара по ID",
    summary="Получение категории товара",
    responses={
        200: {"description": "Категория успешно найдена"},
        404: {"description": "Категория не найдена"},
    }
)
async def get_category_by_id(
    category_id: int,
    db_connect: AsyncSession = Depends(get_db)
) -> ProductCategoryOut:
    # Ищем категорию по ID
    existing_category = (await db_connect.execute(
        select(ProductCategory).filter(ProductCategory.id == category_id)
    )).scalar_one_or_none()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Если категория не удалена, возвращаем данные
    return ProductCategoryOut(
        id=existing_category.id,
        name=existing_category.name,
        description=existing_category.description,
        created_at=existing_category.created_at.isoformat(),
        updated_at=existing_category.updated_at.isoformat()
    )
