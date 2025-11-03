from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Исправляем импорты - используем относительные импорты
from .database import get_db, create_tables
from .crud import StudentManager
from .schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse
)

app = FastAPI(
    title="Student Management API",
    description="CRUD API для управления студентами",
    version="1.0.0"
)

# Создаем таблицы при запуске
@app.on_event("startup")
def startup_event():
    create_tables()

# CRUD Endpoints

@app.post("/students/",
          response_model=StudentResponse,
          status_code=status.HTTP_201_CREATED,
          summary="Создать нового студента")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Создать нового студента
    """
    manager = StudentManager(db)
    return manager.create_student(student.dict())

@app.get("/students/",
         response_model=StudentListResponse,
         summary="Получить всех студентов")
def get_all_students(db: Session = Depends(get_db)):
    """
    Получить список всех студентов
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
    db: Session = Depends(get_db)
):
    """
    Получить студента по ID
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
    db: Session = Depends(get_db)
):
    """
    Обновить данные студента
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
    db: Session = Depends(get_db)
):
    """
    Удалить студента по ID
    """
    manager = StudentManager(db)
    success = manager.delete_student(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )

# Additional endpoints

@app.get("/students/faculty/{faculty}",
         response_model=StudentListResponse,
         summary="Получить студентов по факультету")
def get_students_by_faculty(
    faculty: str,
    db: Session = Depends(get_db)
):
    """
    Получить студентов по названию факультета
    """
    manager = StudentManager(db)
    students = manager.get_students_by_faculty(faculty)
    return {
        "total": len(students),
        "students": students
    }

@app.get("/courses/",
         summary="Получить уникальные курсы")
def get_unique_courses(db: Session = Depends(get_db)):
    """
    Получить список всех уникальных курсов
    """
    manager = StudentManager(db)
    courses = manager.get_unique_courses()
    return {"courses": courses}

@app.get("/faculties/{faculty}/average-grade",
         summary="Получить средний балл по факультету")
def get_average_grade(
    faculty: str,
    db: Session = Depends(get_db)
):
    """
    Получить средний балл по факультету
    """
    manager = StudentManager(db)
    avg_grade = manager.get_average_grade_by_faculty(faculty)
    return {
        "faculty": faculty,
        "average_grade": avg_grade
    }

@app.post("/students/load-csv/",
          summary="Загрузить данные из CSV")
def load_from_csv(db: Session = Depends(get_db)):
    """
    Загрузить данные из CSV файла
    """
    manager = StudentManager(db)
    count = manager.load_from_csv("students.csv")
    return {
        "message": f"Добавлено {count} записей",
        "count": count
    }

@app.delete("/students/",
            summary="Удалить всех студентов")
def delete_all_students(db: Session = Depends(get_db)):
    """
    Удалить всех студентов (очистить базу)
    """
    manager = StudentManager(db)
    count = manager.delete_all_students()
    return {
        "message": f"Удалено {count} студентов",
        "count": count
    }

@app.get("/")
def root():
    return {
        "message": "Student Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}