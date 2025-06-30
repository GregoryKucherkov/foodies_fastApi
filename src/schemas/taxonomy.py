from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class Category(BaseModel):
    name: str


class CategoryResponse(Category):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AreaBase(BaseModel):
    name: str


class AreaResponse(AreaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
