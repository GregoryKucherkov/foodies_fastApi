from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database.db import get_db
from src.schemas.user import TestimonialsResponse
from src.services.testimonials_serv import TestimonialService


router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@router.get("/testimonials", response_model=List[TestimonialsResponse])
async def get_testimonials(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):

    testim_service = TestimonialService(db)
    testimonials = await testim_service.get_testimonials(skip, limit)
    return testimonials
