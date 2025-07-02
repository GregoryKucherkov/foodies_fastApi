from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.recipe import RecipeResponse
from src.database.db import get_db
from src.services.recipe_service import RecipeService
from src.schemas.recipe import RecipeBase, RecipeCreate
from src.schemas.user import Message
from src.services.auth_service import get_current_user
from src.database.user_models import User


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


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    return await recipe_service.create_recipe(data, user)


@router.delete("/{recipe_id}", response_model=RecipeResponse)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    removed_recipe = await recipe_service.delete_recipe(recipe_id, user)
    if not removed_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe is not found!"
        )

    return removed_recipe


@router.get("/my", response_model=List[RecipeResponse])
async def get_own_recipies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    own_recipies = await recipe_service.get_own_recipies(skip, limit, user)
    if not own_recipies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipies are not found!"
        )
    return own_recipies


@router.post("/{recipe_id}/favorite", response_model=RecipeResponse)
async def add_favorite(
    recipe_id,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    favorite = await recipe_service.add_favorite(recipe_id, user)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe is not found!"
        )

    return favorite


@router.delete("/{recipe_id}/favorite", response_model=Message)
async def remove_favorite(
    recipe_id,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    removed_favorite = await recipe_service.remove_favorite(recipe_id, user)
    if not removed_favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe is not found!"
        )

    return {"message": "Favorite removed successfully"}


@router.get("/my/favorite", response_model=List[RecipeResponse])
async def get_my_favorite(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    recipe_service = RecipeService(db)
    my_favorite = recipe_service.get_my_favorite(skip, limit, user)
    if not my_favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No favorite recepies were found!!",
        )
    return my_favorite
