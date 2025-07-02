from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.recipe_repo import RecipeRepo
from typing import List, Optional

from src.schemas.recipe import RecipeBase, RecipeCreate, RecipeUpdate, RecipeResponse
from src.database.user_models import User


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

    async def create_recipe(self, data: RecipeCreate, user: User):
        return await self.recipe_repo.create_recipe(data, user)

    async def delete_recipe(self, recipe_id: int, user: User):
        return await self.recipe_repo.delete_recipe(recipe_id, user)

    async def get_own_recipies(self, skip: int, limit: int, user: User):
        return await self.recipe_repo.get_own_recipies(skip, limit, user)

    async def add_favorite(self, recipe_id: int, user: User):
        return await self.recipe_repo.add_favorite(recipe_id, user)

    async def remove_favorite(self, recipe_id: int, user: User):
        return await self.recipe_repo.remove_favorite(recipe_id, user)

    async def get_my_favorite(self, skip: int, limit: int, user: User):
        return await self.recipe_repo.get_my_favorite(skip, limit, user)
