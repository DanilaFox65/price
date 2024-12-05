from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.dependencies.authentication import get_db
from database.models import ProductCategory
from src.product_category.schemas import ProductCategoryCreate, ProductCategoryOut, ProductCategoriesList

router = APIRouter()


@router.post("/category", response_model=ProductCategoryOut, description="Создание новой категории")
async def create_category(
        category: ProductCategoryCreate,
        db_connect: AsyncSession = Depends(get_db)
):
    # Проверка на уникальность категории
    existing_category = await db_connect.execute(select(ProductCategory).filter(ProductCategory.name == category.name))
    if existing_category.scalars().first():
        raise HTTPException(status_code=400, detail="Категория с таким именем уже существует.")

    db_category = ProductCategory(name=category.name, description=category.description)
    db_connect.add(db_category)
    await db_connect.commit()
    await db_connect.refresh(db_category)
    return db_category


@router.get("/categories", response_model=ProductCategoriesList, description="Получение всех категорий")
async def get_categories(db_connect: AsyncSession = Depends(get_db)):
    result = await db_connect.execute(select(ProductCategory))
    categories = result.scalars().all()
    return ProductCategoriesList(categories=categories)


@router.get("/category/{category_id}", response_model=ProductCategoryOut, description="Получение категории по ID")
async def get_category(category_id: int, db_connect: AsyncSession = Depends(get_db)):
    category = await db_connect.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.put("/category/{category_id}", response_model=ProductCategoryOut, description="Обновление категории")
async def update_category(
        category_id: int,
        category: ProductCategoryCreate,
        db_connect: AsyncSession = Depends(get_db)
):
    db_category = await db_connect.get(ProductCategory, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    db_category.name = category.name
    db_category.description = category.description
    await db_connect.commit()
    await db_connect.refresh(db_category)
    return db_category