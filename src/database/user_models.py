from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Text, Column
from typing import Optional
from src.database.base import Base


class UserFollowers(Base):
    __tablename__ = "userFollowers"

    userId: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    followerId: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    recipes = relationship("Recipe", back_populates="owner")
    testimonials = relationship("Testimonial", back_populates="user")

    followers = relationship(
        "User",
        secondary="userFollowers",
        primaryjoin=id == UserFollowers.userId,
        secondaryjoin=id == UserFollowers.followerId,
        backref="following",
    )

    userFavoriteRecipes = relationship("UserFavoriteRecipe", back_populates="user")
    favoriteRecipes = relationship(
        "Recipe",
        secondary="userFavoriteRecipes",
        back_populates="fans",
        overlaps="userFavoriteRecipes",
    )

    # for logging and debugging
    def __repr__(self):
        return f"User(username={self.name}, email={self.email})"


class UserFavoriteRecipe(Base):
    __tablename__ = "userFavoriteRecipes"

    userId: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    recipeId: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )

    user = relationship(
        "User", back_populates="userFavoriteRecipes", overlaps="favoriteRecipes"
    )
    recipe = relationship(
        "Recipe", back_populates="userFavoriteRecipes", overlaps="fans, favoriteRecipes"
    )


class Testimonial(Base):
    __tablename__ = "testimonials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    testimonial: Mapped[str] = mapped_column(Text, nullable=False)

    userId: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="testimonials")
