from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, Date
from datetime import date
from typing import Optional
from src.database.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    thumb: Mapped[str] = mapped_column(String(255), nullable=False)

    ownerId: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    categoryId: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    owner = relationship("User", back_populates="recipes")
    category = relationship("Category", back_populates="recipes")

    areaId: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False)
    area = relationship("Area", back_populates="recipes")

    recipeIngredients = relationship(
        "RecipeIngredient", back_populates="recipe", overlaps="ingredients"
    )
    ingredients = relationship(
        "Ingredient",
        secondary="recipeIngredients",
        back_populates="recipes",
        overlaps="recipeIngredients",
    )

    userFavoriteRecipes = relationship("UserFavoriteRecipe", back_populates="recipe")
    fans = relationship(
        "User",
        secondary="userFavoriteRecipes",
        back_populates="favoriteRecipes",
        overlaps="user, recipe, userFavoriteRecipes",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipeIngredients"

    recipeId: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredientId: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True
    )

    # If extra fields like quantity:
    measure: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # relationships back to Recipe and Ingredient (optional)
    recipe = relationship(
        "Recipe", back_populates="recipeIngredients", overlaps="ingredients"
    )
    ingredient = relationship(
        "Ingredient",
        back_populates="recipeIngredients",
        overlaps="recipes, ingredients",
    )
