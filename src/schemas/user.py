from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr
    avatar: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TestimonialsBase(BaseModel):
    testimonial: str


class TestimonialsResponse(TestimonialsBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    message: str
