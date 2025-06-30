from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.schemas.taxonomy import AreaResponse

from src.database.db import get_db
from src.services.areas_service import AreaService


router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("/areas", response_model=List[AreaResponse])
async def get_areas(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):

    areas_service = AreaService(db)
    areas = await areas_service.get_areas(skip, limit)

    return areas
