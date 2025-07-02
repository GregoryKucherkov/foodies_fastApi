from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.database.recipe_models import Recipe
from src.database.taxonomy_models import Area, Category
from src.database.ingredient_models import Ingredient
from src.database.user_models import UserFavoriteRecipe, User
from src.schemas.recipe import RecipeCreate
from typing import Optional
from sqlalchemy import and_, func, desc, insert, delete


from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


class RecipeRepo:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def search_recipes(
        self,
        category: Optional[str],
        ingredient: Optional[str],
        area: Optional[str],
        skip,
        limit,
    ) -> List[Recipe]:
        query = select(Recipe).options(
            joinedload(Recipe.category),
            joinedload(Recipe.ingredients),
            joinedload(Recipe.area),
        )

        filters = []

        if category:
            filters.append(Recipe.category.has(Category.name.ilike(f"%{category}%")))
        if ingredient:
            filters.append(
                Recipe.ingredients.any(Ingredient.name.ilike(f"%{ingredient}%"))
            )
        if area:
            filters.append(Recipe.area.has(Area.name.ilike(f"%{area}%")))

        if filters:
            # Combine all filters with AND (all must match)
            query = query.where(and_(*filters))

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def recipe_by_id(self, recipe_id) -> Recipe | None:

        # query = select(Recipe).filter_by(id=recipe_id)

        query = (
            select(Recipe)
            .options(
                joinedload(Recipe.category),
                joinedload(Recipe.ingredients),
                joinedload(Recipe.area),
            )
            .filter_by(id=recipe_id)
        )

        recipe = await self.db.execute(query)

        return recipe.scalar_one_or_none()

    async def popular_recipe(self, skip, limit) -> List[Recipe]:

        query = (
            select(Recipe)
            .join(Recipe.userFavoriteRecipes)
            .group_by(Recipe.id)
            .order_by(desc(func.count(UserFavoriteRecipe.userId)))
            .options(
                joinedload(Recipe.category),
                joinedload(Recipe.area),
                joinedload(Recipe.ingredients),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_recipe(self, data: RecipeCreate, user: User) -> Recipe:
        recipe = Recipe(**data.model_dump(exclude_unset=True), ownerId=user.id)
        self.db.add(recipe)
        await self.db.commit()
        await self.db.refresh(recipe)
        return await self.recipe_by_id(recipe.id)

    async def delete_recipe(self, recipe_id: int, user: User) -> Recipe | None:
        recipe = await self.recipe_by_id(recipe_id)

        if recipe is None or recipe.ownerId != user.id:
            return None

        await self.db.delete(recipe_id)
        await self.db.commit()

        return recipe

    async def get_own_recipies(self, skip: int, limit: int, user: User) -> List[Recipe]:
        query = (
            select(Recipe).where(Recipe.ownerId == user.id).offset(skip).limit(limit)
        )
        recipies = await self.db.execute(query)
        return recipies.scalars().all()

    async def add_favorite(self, recipe_id: int, user: User) -> Recipe | None:

        query = insert(UserFavoriteRecipe).values(
            recipeId=recipe_id,
            userId=user.id,
        )

        await self.db.execute(query)
        await self.db.commit()
        return await self.recipe_by_id(recipe_id)

    async def remove_favorite(self, recipe_id: int, user: User) -> bool:

        query = delete(UserFavoriteRecipe).where(
            UserFavoriteRecipe.recipeId == recipe_id,
            UserFavoriteRecipe.userId == user.id,
        )

        result = await self.db.execute(query)
        await self.db.commit()

        return result.rowcount > 0

    async def get_my_favorite(self, skip: int, limit: int, user: User) -> List[Recipe]:

        query = (
            select(Recipe)
            .join(UserFavoriteRecipe, Recipe.id == UserFavoriteRecipe.recipeId)
            .where(UserFavoriteRecipe.userId == user.id)
            .offset(skip)
            .limit(limit)
        )

        recipies = await self.db.execute(query)
        return recipies.scalars().all()
