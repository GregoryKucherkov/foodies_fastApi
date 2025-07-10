from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from src.database.db import get_db
from src.schemas.user import UserBase, UserOut, UserCreate
from src.schemas.token import TokenRefreshRequest
from src.services.user_service import UserService
from src.services.auth_service import (
    Hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    oath2scheme,
)
from src.config.config import settings
from src.schemas.token import Token
from src.schemas.user import Message
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


# User register
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("15/minute")
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    user = await user_service.get_user_by_email_name(user_data.email, user_data.name)

    if user:
        if user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email is already exists",
            )

        if user.name == user_data.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this name is already exists",
            )

    user_data.password = Hash().get_pass_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("15/minute")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if not user or not Hash().verify_pass(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    access_token = await create_access_token(data={"sub": user.name})
    refresh_token = await create_refresh_token(data={"sub": user.name})
    user.refresh_token = refresh_token
    await db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):

    user = await verify_refresh_token(request.refresh_token, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.name})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=Message)
async def logout_user(
    refresh_token: str = Depends(oath2scheme), db: Session = Depends(get_db)
):

    user = await verify_refresh_token(refresh_token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(db)
    await user_service.user_logout(user)

    return {"message": "Logged out successfully"}
