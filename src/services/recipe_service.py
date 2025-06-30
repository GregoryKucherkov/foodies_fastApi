from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.recipe_repo import RecipeRepo
from typing import List, Optional

from src.schemas.recipe import RecipeBase, RecipeCreate, RecipeUpdate, RecipeResponse


class RecipeService:
    def __init__(self, db: AsyncSession):
        self.recipe_repo = RecipeRepo(db)

    async def search_recipes(
        self,
        category: Optional[str],
        ingredient: Optional[str],
        area: Optional[str],
        skip: int,
        limit: int,
    ):
        return await self.recipe_repo.search_recipes(
            category, ingredient, area, skip, limit
        )

    async def search_by_id(self, recipe_id: int):
        return await self.recipe_repo.recipe_by_id(recipe_id)

    async def get_popular(self, skip: int, limit: int):
        return await self.recipe_repo.popular_recipe(skip, limit)
