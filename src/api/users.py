from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth_service import get_current_user
from src.database.db import get_db
from src.database.user_models import User, UserFollowers
from src.schemas.user import UserBase, UserUpdate
from src.services.upload_file import UploadFileService
from src.services.user_service import UserService
from src.config.config import settings


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserBase)
async def me(user: UserBase = Depends(get_current_user)):
    return user


@router.patch("/{user_id}", response_model=UserUpdate)
async def update_user(
    user_id: int,
    body: UserUpdate,
    user: UserUpdate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if body.avatar:
        user.avatar = body.avatar
    if body.name:
        user.name = body.name
    if body.email:
        user.email = body.email

    updated_user = await user_service.update_user(user)
    return updated_user


@router.patch("/avatar", response_model=UserBase)
async def update_user_avatar(
    file: UploadFile = File(),
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.name)

    user_service = UserService(db)
    updated_user = await user_service.update_avatar_url(user.email, avatar_url)
    return updated_user


@router.get("/following", response_model=List[UserBase])
async def get_following(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    user_service = UserService(db)
    return await user_service.get_user_following(user.id, skip, limit)


@router.get("/followers", responce_model=List[UserBase])
async def get_followers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_service = UserService(db)
    return await user_service.get_followers(user.id, skip, limit)


@router.post("/{to_follow_id}/follow", responce_model=List[UserBase])
async def follow_user(
    to_follow_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if to_follow_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't follow yourself",
        )

    user_service = UserService(db)
    to_follow_user = await user_service.get_user_by_id(to_follow_id)

    if not to_follow_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to follow not found",
        )

    return await user_service.follow_user(user.id, to_follow_id)
