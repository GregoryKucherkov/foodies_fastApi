from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.schemas.user import UserCreate
from src.repo.user_repo import UserRepo
from src.database.user_models import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepo(db)

    async def user_create(self, body: UserCreate):
        avatar: None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        return await self.repo.create_user(body, avatar)

    async def get_user_by_id(self, user_id: str):
        return await self.repo.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        return await self.repo.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        return await self.repo.get_user_by_email(email)

    async def get_user_by_email_name(self, email: str, name: str):
        return await self.repo.get_user_by_email_name(email, name)

    async def create_user(self, body: UserCreate):
        avatar: None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        return await self.repo.create_user(body, avatar)

    async def update_user(self, user: User):
        return await self.repo.update_user(user)

    async def update_avatar_url(self, email: str, avatar: str):
        return await self.repo.update_avatar_url(email, avatar)

    async def user_logout(self, user):
        return await self.repo.user_logout(user)

    async def get_user_following(self, user_id: int, skip: int, limit: int):
        return await self.repo.get_user_following(user_id, skip, limit)

    async def get_followers(self, user_id: int, skip: int, limit: int):
        return await self.repo.get_followers(user_id, skip, limit)

    async def follow_user(self, user_id: int, to_follow_user: int):
        return await self.repo.follow_user(user_id, to_follow_user)

    async def unfollow(self, user_id: int, unfollow_id: int):
        return await self.repo.unfollow(user_id, unfollow_id)
