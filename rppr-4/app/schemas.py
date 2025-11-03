from pydantic import BaseModel, Field
from typing import Optional


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