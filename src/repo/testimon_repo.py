from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select

from src.database.user_models import Testimonial


class TestimonRepo:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_testimonials(self, skip, limit) -> List[Testimonial]:

        query = select(Testimonial).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
