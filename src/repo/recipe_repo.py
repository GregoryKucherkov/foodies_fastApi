from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.database.recipe_models import Recipe
from src.database.taxonomy_models import Area, Category
from src.database.ingredient_models import Ingredient
from src.database.user_models import UserFavoriteRecipe
from typing import Optional
from sqlalchemy import and_, func, desc


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
