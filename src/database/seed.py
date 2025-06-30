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


async def seed_areas(file_path: str, session: AsyncSession):
    with Path(file_path).open("r", encoding="utf-8") as f:
        areas = json.load(f)

    for i in areas:
        area = Area(id=int(i["_id"]["$oid"][-6:], 16), name=i["name"])
        session.add(area)
    await session.commit()


async def seed_categories(file_path: str, session: AsyncSession):
    with Path(file_path).open("r", encoding="utf-8") as f:
        categories = json.load(f)

    for i in categories:
        category = Category(id=int(i["_id"]["$oid"][-6:], 16), name=i["name"])
        session.add(category)
    await session.commit()


async def seed_ingredients(file_path: str, session: AsyncSession):
    with Path(file_path).open("r", encoding="utf-8") as f:
        ingredients = json.load(f)

    created_ingredients = []
    for i in ingredients:
        ingredient = Ingredient(
            # id=int(i["_id"][-6:], 16),
            name=i["name"],
            description=i["desc"],
            imgUrl=i["img"],
        )
        session.add(ingredient)
        created_ingredients.append((i["_id"], ingredient))
    await session.flush()
    ingredient_map = {oid: ing.id for oid, ing in created_ingredients}
    await session.commit()
    return ingredient_map


async def seed_recipies(file_path: str, session: AsyncSession, user_id_map):
    with Path(file_path).open("r", encoding="utf-8") as f:
        recipies = json.load(f)

    for i in recipies:
        area_name = i["area"]
        category_name = i["category"]
        owner_oid = i["owner"]["$oid"]

        # Get Area
        area_id = await session.scalar(select(Area.id).where(Area.name == area_name))
        # Get Category
        category_id = await session.scalar(
            select(Category.id).where(Category.name == category_name)
        )
        # Get Owner
        # owner_id = int(owner_oid, 16)
        owner_id = user_id_map.get(owner_oid)
        if owner_id is None:
            # Skip recipes where owner isn't seeded
            continue

        recipe = Recipe(
            # id=int(i["_id"]["$oid"][-6:], 16),
            title=i["title"],
            description=i["description"],
            instructions=i["instructions"],
            time=int(i["time"] or 0),
            thumb=i["thumb"],
            ownerId=owner_id,
            categoryId=category_id,
            areaId=area_id,
        )
        session.add(recipe)
        await session.flush()

        for ing in i.get("ingredients", []):
            ri = RecipeIngredient(
                recipeId=recipe.id,
                # ingredientId=int(ing["id"][-6:], 16),
                measure=ing.get("measure"),
            )
            session.add(ri)

    await session.commit()


async def seed_testimonials(file_path: str, session: AsyncSession, user_id_map):
    with Path(file_path).open("r", encoding="utf-8") as f:
        testimonials = json.load(f)

    for i in testimonials:
        owner_oid = i["owner"]["$oid"]
        user_id = user_id_map.get(owner_oid)
        if user_id is None:
            continue

        testimonial = Testimonial(
            # id=int(i["_id"]["$oid"][-6:], 16),
            testimonial=i["testimonial"],
            # userId=int(owner_oid, 16),
            userId=user_id,
        )
        session.add(testimonial)
    await session.commit()


# async def seed_user(file_path: str, session: AsyncSession):
#     with Path(file_path).open("r", encoding="utf-8") as f:
#         users = json.load(f)
#         hash_util = Hash()


#         for i in users:
#             user = User(
#                 id=int(i["_id"]["$oid"][-6:], 16),
#                 name=i["name"],
#                 email=i["email"],
#                 avatar=i["avatar"],
#                 hashed_password=hash_util.get_pass_hash(settings.SEED_USER_PASSWORD),
#             )
#             session.add(user)
#         await session.commit()


# Option 2
async def seed_user(file_path: str, session: AsyncSession):
    with Path(file_path).open("r", encoding="utf-8") as f:
        users = json.load(f)
    hash_util = Hash()

    created_users = []
    for i in users:
        user = User(
            name=i["name"],
            email=i["email"],
            avatar=i["avatar"],
            hashed_password=hash_util.get_pass_hash(settings.SEED_USER_PASSWORD),
        )
        session.add(user)
        created_users.append((i["_id"]["$oid"], user))

    await session.flush()

    # Build mapping from original _id to DB id
    oid_to_dbid = {oid: user.id for oid, user in created_users}
    await session.commit()
    return oid_to_dbid


async def clear_existing_data(session: AsyncSession):
    # Delete in reverse dependency order
    # await session.execute(text("DELETE FROM recipe_ingredients"))
    await session.execute(text("DELETE FROM recipes"))
    await session.execute(text("DELETE FROM testimonials"))
    await session.execute(text("DELETE FROM ingredients"))
    await session.execute(text("DELETE FROM categories"))
    await session.execute(text("DELETE FROM areas"))
    await session.execute(text("DELETE FROM users"))
    await session.commit()


async def drop_tables_if_exists(session: AsyncSession):
    # Drop tables in order respecting dependencies (children first)
    drop_statements = [
        "DROP TABLE IF EXISTS recipe_ingredients CASCADE;",
        "DROP TABLE IF EXISTS recipes CASCADE;",
        "DROP TABLE IF EXISTS testimonials CASCADE;",
        "DROP TABLE IF EXISTS ingredients CASCADE;",
        "DROP TABLE IF EXISTS categories CASCADE;",
        "DROP TABLE IF EXISTS areas CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;",
    ]

    for stmt in drop_statements:
        await session.execute(text(stmt))
    await session.commit()


async def main():
    async with sessionmanager.session() as session:

        await clear_existing_data(session)
        print("Deleted!")

        user_id_map = await seed_user(
            str(BASE_DIR / "src" / "database" / "data" / "users.json"), session
        )
        await seed_areas(
            str(BASE_DIR / "src" / "database" / "data" / "areas.json"), session
        )
        await seed_categories(
            str(BASE_DIR / "src" / "database" / "data" / "categories.json"), session
        )
        await seed_recipies(
            str(BASE_DIR / "src" / "database" / "data" / "recipes.json"),
            session,
            user_id_map,
        )
        await seed_testimonials(
            str(BASE_DIR / "src" / "database" / "data" / "testimonials.json"),
            session,
            user_id_map,
        )

    print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
