from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.session import get_db
from database.models import Product, ProductCategory
from src.product.schemas import ProductCreate, ProductOut

router = APIRouter()


@router.post("/product", response_model=ProductOut, description="Создание нового продукта")
async def create_product(
        product: ProductCreate,
        db_connect: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли категория
    category = await db_connect.get(ProductCategory, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена.")

    # Создание продукта
    db_product = Product(
        name=product.name,
        description=product.description,
        category_id=product.category_id
    )
    db_connect.add(db_product)
    await db_connect.commit()
    await db_connect.refresh(db_product)
    return db_product