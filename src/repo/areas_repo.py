from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select

from src.database.taxonomy_models import Area


class AreasRepo:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_areas(self, skip, limit) -> List[Area]:

        query = select(Area).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
