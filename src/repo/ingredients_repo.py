from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select

from src.database.ingredient_models import Ingredient


class IngredRepo:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_ingredients(self, skip, limit) -> List[Ingredient]:

        query = select(Ingredient).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all()
