from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .database import get_db, create_tables
from .crud import StudentManager
from .schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse
)
from .auth_router import router as auth_router
from .dependencies import get_current_user
from .schemas import UserResponse

app = FastAPI(
    title="Student Management API",
    description="CRUD API для управления студентами с аутентификацией",
    version="2.0.0"
)

# Подключаем роутер аутентификации
app.include_router(auth_router)

# Создаем таблицы при запуске
@app.on_event("startup")
def startup_event():
    create_tables()

# Защищенные эндпоинты (требуют аутентификации)

@app.post("/students/",
          response_model=StudentResponse,
          status_code=status.HTTP_201_CREATED,
          summary="Создать нового студента")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Создать нового студента (требует авторизации)
    """
    manager = StudentManager(db)
    return manager.create_student(student.dict())

@app.get("/students/",
         response_model=StudentListResponse,
         summary="Получить всех студентов")
def get_all_students(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить список всех студентов (требует авторизации)
    """
    manager = StudentManager(db)
    students = manager.get_all_students()
    return {
        "total": len(students),
        "students": students
    }

@app.get("/students/{student_id}",
         response_model=StudentResponse,
         summary="Получить студента по ID")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить студента по ID (требует авторизации)
    """
    manager = StudentManager(db)
    student = manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )
    return student

@app.put("/students/{student_id}",
         response_model=StudentResponse,
         summary="Обновить данные студента")
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Обновить данные студента (требует авторизации)
    """
    manager = StudentManager(db)
    student = manager.update_student(student_id, student_data)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )
    return student

@app.delete("/students/{student_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить студента")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Удалить студента по ID (требует авторизации)
    """
    manager = StudentManager(db)
    success = manager.delete_student(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )

# Дополнительные защищенные эндпоинты

@app.get("/students/faculty/{faculty}",
         response_model=StudentListResponse,
         summary="Получить студентов по факультету")
def get_students_by_faculty(
    faculty: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить студентов по названию факультета (требует авторизации)
    """
    manager = StudentManager(db)
    students = manager.get_students_by_faculty(faculty)
    return {
        "total": len(students),
        "students": students
    }

@app.get("/courses/",
         summary="Получить уникальные курсы")
def get_unique_courses(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить список всех уникальных курсов (требует авторизации)
    """
    manager = StudentManager(db)
    courses = manager.get_unique_courses()
    return {"courses": courses}

@app.get("/faculties/{faculty}/average-grade",
         summary="Получить средний балл по факультету")
def get_average_grade(
    faculty: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить средний балл по факультету (требует авторизации)
    """
    manager = StudentManager(db)
    avg_grade = manager.get_average_grade_by_faculty(faculty)
    return {
        "faculty": faculty,
        "average_grade": avg_grade
    }

@app.post("/students/load-csv/",
          summary="Загрузить данные из CSV")
def load_from_csv(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Загрузить данные из CSV файла (требует авторизации)
    """
    manager = StudentManager(db)
    count = manager.load_from_csv("students.csv")
    return {
        "message": f"Добавлено {count} записей",
        "count": count
    }

@app.delete("/students/",
            summary="Удалить всех студентов")
def delete_all_students(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Удалить всех студентов (очистить базу) (требует авторизации)
    """
    manager = StudentManager(db)
    count = manager.delete_all_students()
    return {
        "message": f"Удалено {count} студентов",
        "count": count
    }

# Открытые эндпоинты (не требуют аутентификации)
@app.get("/")
def root():
    return {
        "message": "Student Management API с аутентификацией",
        "version": "2.0.0",
        "docs": "/docs",
        "auth_endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "logout": "POST /auth/logout",
            "me": "GET /auth/me"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}