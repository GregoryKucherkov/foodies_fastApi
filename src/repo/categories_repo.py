from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select

from src.database.taxonomy_models import Category


class CategoryRepo:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_categories(self, skip, limit) -> List[Category]:

        query = select(Category).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
