from fastapi import APIRouter
from src.user.router import router as users_router
from src.product.router import router as product_router
from src.product_category.router import router as product_category_router

api_router = APIRouter()

api_router.include_router(users_router, tags=["user"])
api_router.include_router(product_router, tags=["product"])
api_router.include_router(product_category_router, tags=["category"])
