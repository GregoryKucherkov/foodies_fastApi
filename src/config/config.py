from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


# class Config:
#     DB_URL = "postgresql://foodies_db_9vfz_user:v1DVZ7iJxFzACizCcMMfp9dAfHFNppjr@dpg-d15evmfdiees73fvnju0-a.frankfurt-postgres.render.com/foodies_db_9vfz"
# postgresql://foodies_db_9vfz_user:v1DVZ7iJxFzACizCcMMfp9dAfHFNppjr@dpg-d15evmfdiees73fvnju0-a.frankfurt-postgres.render.com/foodies_db_9vfz


# config = Config


class Settings(BaseSettings):

    DB_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    # JWT_EXPIRATION_SECONDS: int

    REFRESH_TOKEN_EXPIRE_MINUTES: int  # 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    SEED_USER_PASSWORD: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
