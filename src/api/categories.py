from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.db import get_db
from src.schemas.taxonomy import CategoryResponse
from src.services.categories_service import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    cat_service = CategoryService(db)
    categories = await cat_service.get_categories(skip, limit)
    return categories
