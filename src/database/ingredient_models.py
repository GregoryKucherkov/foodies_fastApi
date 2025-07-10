from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from typing import Optional
from src.database.base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    imgUrl: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Back reference to join table
    recipeIngredients = relationship("RecipeIngredient", back_populates="ingredient")
    # Many to many relationship to Recipe through join table
    recipes = relationship(
        "Recipe",
        secondary="recipeIngredients",
        back_populates="ingredients",
        overlaps="ingredient, recipe, recipeIngredients, ingredients",
    )
