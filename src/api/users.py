from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth_service import get_current_user
from src.database.db import get_db
from src.database.user_models import User, UserFollowers
from src.schemas.user import UserBase, UserOut, UserUpdate, Message
from src.services.upload_file import UploadFileService
from src.services.user_service import UserService
from src.config.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserOut)
@limiter.limit("15/minute")
async def me(user: UserBase = Depends(get_current_user)):
    return user


@router.patch("/me/avatar", response_model=UserOut)
async def update_user_avatar(
    file: UploadFile = File(),
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    avatar_url = await UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.name)

    user_service = UserService(db)
    updated_user = await user_service.update_avatar_url(user.email, avatar_url)

    return updated_user


@router.get("/me/following", response_model=List[UserOut])
async def get_following(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    user_service = UserService(db)
    return await user_service.get_user_following(user.id, skip, limit)


@router.get("/me/followers", response_model=List[UserOut])
async def get_followers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_service = UserService(db)
    return await user_service.get_followers(user.id, skip, limit)


@router.patch("/me", response_model=UserUpdate)
async def update_me(
    body: UserUpdate,
    user: UserUpdate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user.id)
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


@router.post("/{to_follow_id:int}/follow", response_model=Message)
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


@router.delete("/{unfollow_id:int}/unfollow", response_model=Message)
async def unfollow_user(
    unfollow_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if unfollow_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't follow yourself",
        )

    user_service = UserService(db)
    unfollow = await user_service.get_user_by_id(unfollow_id)

    if not unfollow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return await user_service.unfollow(user.id, unfollow_id)
