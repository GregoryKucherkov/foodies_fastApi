from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.areas_repo import AreasRepo


class AreaService:
    def __init__(self, db: AsyncSession):
        self.areas_repo = AreasRepo(db)

    async def get_areas(self, skip: int, limit: int):
        return await self.areas_repo.get_areas(skip, limit)
