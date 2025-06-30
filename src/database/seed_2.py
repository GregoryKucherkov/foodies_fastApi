import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import json
from src.database.taxonomy_models import Area, Category
from src.database.recipe_models import Recipe, RecipeIngredient
from src.database.ingredient_models import Ingredient
from src.database.user_models import Testimonial, User
from src.database.db import sessionmanager
from src.services.auth_service import Hash
from src.config.config import settings

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

import asyncio
from sqlalchemy.future import select


class Seeder:
    def __init__(self):
        self.data_path = BASE_DIR / "src" / "database" / "data"
        self.hash = Hash()
        self.id_maps = {
            "users": {},
            "ingredients": {},
            "areas": {},
            "categories": {},
            "recipes": {},
        }

    async def _load_data(self, filename: str) -> list:
        """Load JSON data from file"""
        with open(self.data_path / filename, "r", encoding="utf-8") as f:
            return json.load(f)

    async def _clear_tables(self, session: AsyncSession):
        """Clear all tables in proper order"""
        tables = [
            "userFavoriteRecipes",
            "userFollowers",
            "recipeIngredients",
            "testimonials",
            "recipes",
            "ingredients",
            "categories",
            "areas",
            "users",
        ]
        for table in tables:
            # await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            try:
                await session.execute(
                    text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
                )
            except Exception as e:
                print(f"⚠️ Skipping {table} (might not exist): {e}")
        print("🧹 All listed tables truncated. IDs restarted.")

    async def seed_users(self, session: AsyncSession):
        """Seed users with hardcoded password for accessibility"""
        users = await self._load_data("users.json")
        for user in users:
            original_id = user["_id"]["$oid"]
            db_user = User(
                name=user["name"],
                email=user["email"],
                avatar=user["avatar"],
                hashed_password=self.hash.get_pass_hash("test123"),  # Hardcoded
            )
            session.add(db_user)
            await session.flush()
            self.id_maps["users"][original_id] = db_user.id

    async def seed_areas(self, session: AsyncSession):
        """Seed areas"""
        areas = await self._load_data("areas.json")
        for area in areas:
            db_area = Area(name=area["name"])
            session.add(db_area)
            await session.flush()
            # self.id_maps["areas"][area["_id"]["$oid"]] = db_area.id
            self.id_maps["areas"][area["name"]] = db_area.id

    async def seed_categories(self, session: AsyncSession):
        """Seed categories"""
        categories = await self._load_data("categories.json")
        for category in categories:
            db_category = Category(name=category["name"])
            session.add(db_category)
            await session.flush()
            # self.id_maps["categories"][category["_id"]["$oid"]] = db_category.id
            self.id_maps["categories"][category["name"]] = db_category.id

    async def seed_ingredients(self, session: AsyncSession):
        """Seed ingredients"""
        ingredients = await self._load_data("ingredients.json")
        for ingredient in ingredients:
            db_ingredient = Ingredient(
                name=ingredient["name"],
                description=ingredient["desc"],
                imgUrl=ingredient["img"],
            )
            session.add(db_ingredient)
            await session.flush()
            self.id_maps["ingredients"][ingredient["_id"]] = db_ingredient.id

    async def seed_recipes(self, session: AsyncSession):
        """Seed recipes with their relationships"""
        recipes = await self._load_data("recipes.json")

        missing_count = {"owner": 0, "area": 0, "category": 0}

        for recipe in recipes:
            # Validate required relationships exist
            owner_id = self.id_maps["users"].get(recipe["owner"]["$oid"])
            area_id = self.id_maps["areas"].get(recipe["area"])
            category_id = self.id_maps["categories"].get(recipe["category"])

            # if not all([owner_id, area_id, category_id]):
            #     print("relationship is missing")
            #     continue  # Skip if any relationship is missing

            if not owner_id:
                print(
                    f"Missing owner: {recipe['owner']['$oid']} for recipe {recipe['title']}"
                )
                missing_count["owner"] += 1
                continue

            if not area_id:
                print(f"Missing area: {recipe['area']} for recipe {recipe['title']}")
                missing_count["area"] += 1
                continue

            if not category_id:
                print(
                    f"Missing category: {recipe['category']} for recipe {recipe['title']}"
                )
                missing_count["category"] += 1
                continue

            db_recipe = Recipe(
                title=recipe["title"],
                instructions=recipe["instructions"],
                description=recipe["description"],
                thumb=recipe["thumb"],
                time=int(recipe["time"] or 0),
                ownerId=owner_id,
                areaId=area_id,
                categoryId=category_id,
            )
            session.add(db_recipe)
            await session.flush()
            self.id_maps["recipes"][recipe["_id"]["$oid"]] = db_recipe.id

            # Handle recipe ingredients
            for ingredient in recipe.get("ingredients", []):
                ing_id = self.id_maps["ingredients"].get(ingredient["id"])
                if ing_id:
                    session.add(
                        RecipeIngredient(
                            recipeId=db_recipe.id,
                            ingredientId=ing_id,
                            measure=ingredient["measure"],
                        )
                    )
        print("\nMissing relationships summary:")
        print(f"Owners: {missing_count['owner']}")
        print(f"Areas: {missing_count['area']}")
        print(f"Categories: {missing_count['category']}")

    async def seed_testimonials(self, session: AsyncSession):
        """Seed testimonials"""
        testimonials = await self._load_data("testimonials.json")
        for testimonial in testimonials:
            user_id = self.id_maps["users"].get(testimonial["owner"]["$oid"])
            if user_id:
                session.add(
                    Testimonial(testimonial=testimonial["testimonial"], userId=user_id)
                )

    async def run(self):
        """Execute the seeding process"""
        async with sessionmanager.session() as session:
            async with session.begin():
                try:
                    await self._clear_tables(session)

                    # Seed in proper dependency order
                    await self.seed_users(session)
                    await self.seed_areas(session)
                    await self.seed_categories(session)
                    await self.seed_ingredients(session)
                    await self.seed_recipes(session)
                    await self.seed_testimonials(session)

                    print("✅ Database seeded successfully!")
                except Exception as e:
                    await session.rollback()
                    print(f"❌ Seeding failed: {e}")
                    raise


if __name__ == "__main__":
    seeder = Seeder()
    asyncio.run(seeder.run())
