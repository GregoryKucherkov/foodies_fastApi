from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from sqlalchemy.future import select
from sqlalchemy import or_, insert, delete

from src.database.user_models import (
    User,
    UserFollowers,
    UserFavoriteRecipe,
    UserFollowers,
)
from src.schemas.user import UserCreate


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).filter(User.id == user_id)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:

        query = select(User).filter_by(email=email)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_email_name(self, email_hash, name) -> User | None:

        query = select(User).where(or_(User.email == email_hash, User.name == name))

        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username) -> User | None:
        query = select(User).filter_by(name=username)
        user = await self.db.execute(query)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: User) -> User:
        from src.services import auth_service

        self.db.add(user)
        await self.db.commit()
        username = user.name
        auth_service.red.delete(f"user:{username}")
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: str, avatar_url: str) -> User:
        from src.services import auth_service

        user = await self.get_user_by_email(email)
        user.avatar = avatar_url
        await self.db.commit()
        username = user.name
        auth_service.red.delete(f"user:{username}")
        await self.db.refresh(user)

        return user

    async def user_logout(self, user: User) -> None:
        user.refresh_token = None
        await self.db.commit()
        await self.db.refresh(user)

    async def get_user_following(self, user_id, skip, limit) -> List[User]:
        query = (
            select(User)
            .join(UserFollowers, User.id == UserFollowers.followerId)
            .where(UserFollowers.userId == user_id)
            .offset(skip)
            .limit(limit)
        )

        following = await self.db.execute(query)
        return following.scalars().all()

    async def get_followers(self, user_id, skip, limit) -> List[User]:
        query = (
            select(User)
            .join(UserFollowers, User.id == UserFollowers.userId)
            .where(UserFollowers.followerId == user_id)
            .offset(skip)
            .limit(limit)
        )

        followers = await self.db.execute(query)
        return followers.scalars().all()

    async def follow_user(self, user_id, to_follow_user):
        existing = await self.db.execute(
            select(UserFollowers).where(
                UserFollowers.userId == user_id,
                UserFollowers.followerId == to_follow_user,
            )
        )
        if existing.scalar_one_or_none():
            return

        follow = UserFollowers(userId=user_id, followerId=to_follow_user)

        self.db.add(follow)
        await self.db.commit()
        await self.db.refresh(follow)
        return {"message": "The user followed"}

    async def unfollow(self, user_id, unfollow_id):

        query = delete(UserFollowers).where(
            UserFollowers.userId == user_id,
            UserFollowers.followerId == unfollow_id,
        )
        await self.db.execute(query)
        await self.db.commit()

        return {"message": "The user has been unfollowed"}
