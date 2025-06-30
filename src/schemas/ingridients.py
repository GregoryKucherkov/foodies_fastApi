from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class IngredientBase(BaseModel):
    name: str
    description: str
    imgUrl: Optional[str] = None


class IngredientResponse(IngredientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
