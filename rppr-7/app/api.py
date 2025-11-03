from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import asyncio

from .database import get_db, create_tables
from .crud import StudentManager
from .schemas import (
    StudentCreate, StudentUpdate, StudentResponse, StudentListResponse,
    CSVLoadRequest, DeleteStudentsRequest, BackgroundTaskResponse,
    CSVLoadResponse, DeleteStudentsResponse, CacheStatsResponse
)
from .auth_router import router as auth_router
from .dependencies import get_current_user
from .schemas import UserResponse
from .background_tasks import load_students_from_csv, delete_students_by_ids, delete_all_students
from .cache import cache, cached, invalidate_cache

app = FastAPI(
    title="Student Management API",
    description="CRUD API для управления студентами с аутентификацией, кешированием и фоновыми задачами",
    version="3.0.0"
)

# Подключаем роутер аутентификации
app.include_router(auth_router)


# Создаем таблицы при запуске
@app.on_event("startup")
def startup_event():
    create_tables()


# Хранилище для отслеживания фоновых задач (в продакшене используйте Redis или БД)
background_tasks = {}


# Защищенные эндпоинты с кешированием

@app.post("/students/",
          response_model=StudentResponse,
          status_code=status.HTTP_201_CREATED,
          summary="Создать нового студента")
@invalidate_cache("students:*")
async def create_student(
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
@cached("students:all", expire=300)
async def get_all_students(
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить список всех студентов (требует авторизации, кешируется)
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
@cached("students:{student_id}", expire=300)
async def get_student(
        student_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить студента по ID (требует авторизации, кешируется)
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
@invalidate_cache("students:*")
async def update_student(
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
@invalidate_cache("students:*")
async def delete_student(
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


# Дополнительные защищенные эндпоинты с кешированием

@app.get("/students/faculty/{faculty}",
         response_model=StudentListResponse,
         summary="Получить студентов по факультету")
@cached("students:faculty:{faculty}", expire=300)
async def get_students_by_faculty(
        faculty: str,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить студентов по названию факультета (требует авторизации, кешируется)
    """
    manager = StudentManager(db)
    students = manager.get_students_by_faculty(faculty)
    return {
        "total": len(students),
        "students": students
    }


@app.get("/courses/",
         summary="Получить уникальные курсы")
@cached("courses:all", expire=600)
async def get_unique_courses(
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить список всех уникальных курсов (требует авторизации, кешируется)
    """
    manager = StudentManager(db)
    courses = manager.get_unique_courses()
    return {"courses": courses}


@app.get("/faculties/{faculty}/average-grade",
         summary="Получить средний балл по факультету")
@cached("faculties:average:{faculty}", expire=600)
async def get_average_grade(
        faculty: str,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить средний балл по факультету (требует авторизации, кешируется)
    """
    manager = StudentManager(db)
    avg_grade = manager.get_average_grade_by_faculty(faculty)
    return {
        "faculty": faculty,
        "average_grade": avg_grade
    }


# Эндпоинты для фоновых задач

@app.post("/background/load-csv",
          response_model=BackgroundTaskResponse,
          summary="Загрузить данные из CSV (фоновая задача)")
async def background_load_csv(
        request: CSVLoadRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Загрузить данные из CSV файла в фоновом режиме
    """
    task_id = str(uuid.uuid4())

    async def run_task():
        result = await load_students_from_csv(db, request.csv_file_path)
        background_tasks[task_id] = {
            "status": "completed",
            "result": result
        }

    # Запускаем фоновую задачу
    background_tasks.add_task(run_task)

    background_tasks[task_id] = {
        "status": "running",
        "result": None
    }

    return BackgroundTaskResponse(
        task_id=task_id,
        status="running",
        message="Задача загрузки CSV запущена в фоновом режиме"
    )


@app.post("/background/delete-students",
          response_model=BackgroundTaskResponse,
          summary="Удалить студентов по ID (фоновая задача)")
async def background_delete_students(
        request: DeleteStudentsRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Удалить студентов по списку ID в фоновом режиме
    """
    task_id = str(uuid.uuid4())

    async def run_task():
        result = await delete_students_by_ids(db, request.student_ids)
        background_tasks[task_id] = {
            "status": "completed",
            "result": result
        }

    # Запускаем фоновую задачу
    background_tasks.add_task(run_task)

    background_tasks[task_id] = {
        "status": "running",
        "result": None
    }

    return BackgroundTaskResponse(
        task_id=task_id,
        status="running",
        message="Задача удаления студентов запущена в фоновом режиме"
    )


@app.get("/background/tasks/{task_id}",
         summary="Получить статус фоновой задачи")
async def get_background_task_status(
        task_id: str,
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить статус выполнения фоновой задачи
    """
    task_info = background_tasks.get(task_id)

    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    if task_info["status"] == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task_info["result"]
        }
    else:
        return {
            "task_id": task_id,
            "status": "running",
            "result": None
        }


# Управление кешем

@app.post("/cache/clear",
          summary="Очистить кеш")
async def clear_cache(
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Очистить весь кеш Redis
    """
    success = cache.flush_all()
    return {
        "success": success,
        "message": "Кеш очищен" if success else "Ошибка при очистке кеша"
    }


@app.get("/cache/stats",
         response_model=CacheStatsResponse,
         summary="Получить статистику кеша")
async def get_cache_stats(
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получить статистику Redis кеша
    """
    try:
        # Простая статистика (в реальном приложении можно использовать redis.info())
        keys = cache.redis_client.keys('*')
        memory_info = cache.redis_client.info('memory')

        return CacheStatsResponse(
            total_keys=len(keys),
            memory_usage=f"{memory_info.get('used_memory_human', 'N/A')}",
            connected_clients=memory_info.get('connected_clients', 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики кеша: {str(e)}"
        )


# Открытые эндпоинты (не требуют аутентификации)
@app.get("/")
async def root():
    return {
        "message": "Student Management API с аутентификацией, кешированием и фоновыми задачами",
        "version": "3.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    # Проверяем подключение к Redis
    redis_healthy = False
    try:
        redis_healthy = cache.redis_client.ping()
    except:
        pass

    return {
        "status": "healthy",
        "redis": "connected" if redis_healthy else "disconnected"
    }