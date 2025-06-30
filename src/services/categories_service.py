from sqlalchemy.ext.asyncio import AsyncSession
from src.repo.categories_repo import CategoryRepo


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.catagory_repo = CategoryRepo(db)

    async def get_categories(self, skip: int, limit: int):
        return await self.catagory_repo.get_categories(skip, limit)
