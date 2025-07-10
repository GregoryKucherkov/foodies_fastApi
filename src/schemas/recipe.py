from pydantic import BaseModel, ConfigDict
from typing import Optional


class RecipeBase(BaseModel):
    title: str
    description: str
    instructions: str
    thumb: Optional[str] = None


class RecipeCreate(RecipeBase):
    categoryId: int
    areaId: int


class RecipeUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    instructions: Optional[str]
    thumb: Optional[str] = None


class RecipeResponse(RecipeBase):
    id: int
    ownerId: int
    categoryId: int
    areaId: int

    model_config = ConfigDict(from_attributes=True)
