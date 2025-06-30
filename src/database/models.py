# from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
# from sqlalchemy import Integer, Column, String, Text, ForeignKey, PrimaryKeyConstraint
# from typing import Optional


# class Base(DeclarativeBase):
#     pass


# class RecipeIngredient(Base):
#     __tablename__ = "recipeIngredients"

#     recipeId: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
#     ingredientId: Mapped[int] = mapped_column(
#         ForeignKey("ingredients.id"), primary_key=True
#     )

#     # If you want extra fields like quantity, add here
#     # amount: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

#     # relationships back to Recipe and Ingredient (optional but recommended)
#     recipe = relationship("Recipe", back_populates="recipeIngredients")
#     ingredient = relationship("Ingredient", back_populates="recipeIngredients")


# class UserFavoriteRecipe(Base):
#     __tablename__ = "userFavoriteRecipes"

#     userId: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
#     recipeId: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

#     user = relationship("User", back_populates="userFavoriteRecipes")
#     recipe = relationship("Recipe", back_populates="userFavoriteRecipes")


# class UserFollowers(Base):
#     __tablename__ = "userFollowers"

#     userId: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
#     followerId: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(50), unique=True)
#     email: Mapped[str] = mapped_column(String(100), unique=True)
#     # hashed_password: Mapped[str] = Column(String)
#     hashed_password: Mapped[str] = mapped_column(String)

#     # avatar = Column(String(255), nullable=True)
#     avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

#     token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

#     recipes = relationship("Recipe", back_populates="owner")
#     testimonials = relationship("Testimonial", back_populates="user")

#     followers = relationship(
#         "User",
#         secondary="userFollowers",
#         primaryjoin=id == UserFollowers.userId,
#         secondaryjoin=id == UserFollowers.followerId,
#         backref="following",
#     )

#     userFavoriteRecipes = relationship("UserFavoriteRecipe", back_populates="user")
#     favoriteRecipes = relationship(
#         "Recipe",
#         secondary="userFavoriteRecipes",
#         back_populates="fans",
#     )


# class Category(Base):
#     __tablename__ = "categories"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)

#     recipes = relationship("Recipe", back_populates="category")


# class Area(Base):
#     __tablename__ = "areas"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)

#     recipes = relationship("Recipe", back_populates="area")


# class Ingredient(Base):
#     __tablename__ = "ingredients"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[str] = mapped_column(String(255), nullable=False)
#     imgUrl: Mapped[Optional[str]] = mapped_column(String, nullable=True)

#     # Back reference to join table
#     recipeIngredients = relationship("RecipeIngredient", back_populates="ingredient")
#     # Many to many relationship to Recipe through join table
#     recipes = relationship(
#         "Recipe",
#         secondary="recipeIngredients",
#         back_populates="ingredients",
#     )


# class Testimonial(Base):
#     __tablename__ = "testimonials"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     testimonial: Mapped[str] = mapped_column(String(255), nullable=False)

#     userId: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     user = relationship("User", back_populates="testimonials")


# class Recipe(Base):
#     __tablename__ = "recipes"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     title: Mapped[str] = mapped_column(String(255), nullable=False)
#     description: Mapped[str] = mapped_column(Text, nullable=False)
#     instructions: Mapped[str] = mapped_column(Text, nullable=False)
#     thumb: Mapped[str] = mapped_column(String(255), nullable=False)

#     ownerId: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
#     categoryId: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

#     owner = relationship("User", back_populates="recipes")
#     category = relationship("Category", back_populates="recipes")

#     areaId: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False)
#     area = relationship("Area", back_populates="recipes")

#     recipeIngredients = relationship("RecipeIngredient", back_populates="recipe")
#     ingredients = relationship(
#         "Ingredient",
#         secondary="recipeIngredients",
#         back_populates="recipes",
#     )

#     userFavoriteRecipes = relationship("UserFavoriteRecipe", back_populates="recipe")
#     fans = relationship(
#         "User",
#         secondary="userFavoriteRecipes",
#         back_populates="favoriteRecipes",
#     )
