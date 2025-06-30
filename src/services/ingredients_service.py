from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.ingredients_repo import IngredRepo


class IngredService:

    def __init__(self, db: AsyncSession):
        self.ingred_repo = IngredRepo(db)

    async def get_ingredients(self, skip: int, limit: int):
        return await self.ingred_repo.get_ingredients(skip, limit)
