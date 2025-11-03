from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# Student schemas
class StudentBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя")
    faculty: str = Field(..., min_length=1, max_length=50, description="Факультет")
    course: str = Field(..., min_length=1, max_length=100, description="Курс")
    grade: int = Field(..., ge=0, le=100, description="Оценка")


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Фамилия")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Имя")
    faculty: Optional[str] = Field(None, min_length=1, max_length=50, description="Факультет")
    course: Optional[str] = Field(None, min_length=1, max_length=100, description="Курс")
    grade: Optional[int] = Field(None, ge=0, le=100, description="Оценка")


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    total: int
    students: list[StudentResponse]


# Auth schemas (новые)
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email адрес")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль")


class UserLogin(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class LogoutResponse(BaseModel):
    message: str