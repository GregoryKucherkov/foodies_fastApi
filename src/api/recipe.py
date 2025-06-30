from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.recipe import RecipeResponse
from src.database.db import get_db
from src.services.recipe_service import RecipeService


router = APIRouter(prefix="/recipe", tags=["recipe"])


# Public endpoints
@router.get("/search/", response_model=List[RecipeResponse])
async def search_recipes(
    category: Optional[str],
    ingredient: Optional[str],
    area: Optional[str],
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):

    recipe_service = RecipeService(db)
    recipes = await recipe_service.search_recipes(
        category=category,
        ingredient=ingredient,
        area=area,
        skip=skip,
        limit=limit,
    )
    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipes with you criteria wasn`t found!",
        )
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def search_recipe_id(recipe_id: int, db: AsyncSession = Depends(get_db)):

    recipe_service = RecipeService(db)
    recipe = await recipe_service.search_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipes with you criteria wasn`t found!",
        )
    return recipe


@router.get("/popular", response_model=List[RecipeResponse])
async def get_popular(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):

    recipe_service = RecipeService(db)
    recipes = await recipe_service.get_popular(skip, limit)
    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recepies were found!",
        )

    return recipes


# Private endoints
