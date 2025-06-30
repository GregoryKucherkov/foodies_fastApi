from datetime import datetime, timedelta, UTC
from typing import Optional, Literal

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from src.config.config import settings
from src.database.db import get_db
from src.services.user_service import UserService


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_pass(self, plain_pass, hashed_pass):
        return self.pwd_context.verify(plain_pass, hashed_pass)

    def get_pass_hash(self, password: str):
        return self.pwd_context.hash(password)

    # def get_email_hash(self, email: str):
    #     return self.pwd_context.hash(email)


oath2scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_token(
    data: dict, expires_delta: timedelta, token_type: Literal["access", "refresh"]
):
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta

    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})

    encode_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encode_jwt


async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    if expires_delta:
        access_token = await create_token(data, expires_delta, "access")
    else:
        access_token = await create_token(
            data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access"
        )
    return access_token


async def create_refresh_token(data: dict, expires_delta: Optional[int] = None):
    if expires_delta:
        refresh_token = await create_token(data, expires_delta, "refresh")
    else:
        refresh_token = await create_token(
            data, timedelta(seconds=settings.JWT_EXPIRATION_SECONDS), "refresh"
        )
    return refresh_token


async def get_current_user(
    token: str = Depends(oath2scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": " Bearer"},
    )
    try:
        # decode jwt
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        token_type: str = payload.get("token_type")
        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception
    return user


async def verify_refresh_token(refresh_token: str, db: Session):
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload["sub"]
        token_type: str = payload["token_type"]
        if username is None or token_type != "refresh":
            return None
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        stored_refresh_token = user.refresh_token

        if stored_refresh_token != refresh_token:
            return None

        return user

    except JWTError:
        return None
