from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.schemas.ingridients import IngredientResponse

from src.database.db import get_db
from src.services.ingredients_service import IngredService


router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_ingredients(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):

    ingred_service = IngredService(db)
    ingredients = await ingred_service.get_ingredients(skip, limit)
    return ingredients
