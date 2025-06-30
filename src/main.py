from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.api import (
    utils,
    recipe,
    testimonials,
    ingredients,
    areas,
    categories,
    auth,
    users,
)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(recipe.router, prefix="/api")
app.include_router(testimonials.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")
app.include_router(areas.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Foodies!"}


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
