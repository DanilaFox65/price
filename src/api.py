from fastapi import APIRouter
from src.user.router import router as users_router
from src.product_category.router import router as product_category_router
from src.product.router import router as product_router
from src.shop.router import router as shops_router
from src.products_In_store.router import router as products_In_store
api_router = APIRouter()

api_router.include_router(users_router, tags=["user"])
api_router.include_router(product_category_router, tags=["category"])
api_router.include_router(product_router, tags=["product"])
api_router.include_router(shops_router, tags=["shop"])
api_router.include_router(products_In_store, tags=["Products In Store"])