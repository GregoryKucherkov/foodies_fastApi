from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.testimon_repo import TestimonRepo


class TestimonialService:
    def __init__(self, db: AsyncSession):
        self.testim_repo = TestimonRepo(db)

    async def get_testimonials(self, skip: int, limit: int):
        return await self.testim_repo.get_testimonials(skip, limit)
