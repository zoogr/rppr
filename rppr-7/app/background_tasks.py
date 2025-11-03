import csv
import os
from typing import List
from sqlalchemy.orm import Session
from .crud import StudentManager
from .cache import cache


async def load_students_from_csv(db: Session, csv_file_path: str):
    """
    Фоновая задача для загрузки студентов из CSV файла
    """
    try:
        if not os.path.exists(csv_file_path):
            return {"success": False, "message": f"Файл {csv_file_path} не найден", "count": 0}

        manager = StudentManager(db)
        count = manager.load_from_csv(csv_file_path)

        # Инвалидируем кеш после загрузки новых данных
        cache.delete_pattern("students:*")
        cache.delete_pattern("courses:*")
        cache.delete_pattern("faculties:*")

        return {
            "success": True,
            "message": f"Успешно загружено {count} записей из {csv_file_path}",
            "count": count
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при загрузке CSV: {str(e)}",
            "count": 0
        }


async def delete_students_by_ids(db: Session, student_ids: List[int]):
    """
    Фоновая задача для удаления студентов по списку ID
    """
    try:
        manager = StudentManager(db)
        deleted_count = 0

        for student_id in student_ids:
            success = manager.delete_student(student_id)
            if success:
                deleted_count += 1

        # Инвалидируем кеш после удаления
        cache.delete_pattern("students:*")
        cache.delete_pattern("courses:*")
        cache.delete_pattern("faculties:*")

        return {
            "success": True,
            "message": f"Успешно удалено {deleted_count} студентов из {len(student_ids)} запрошенных",
            "deleted_count": deleted_count,
            "requested_count": len(student_ids)
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при удалении студентов: {str(e)}",
            "deleted_count": 0,
            "requested_count": len(student_ids)
        }


async def delete_all_students(db: Session):
    """
    Фоновая задача для удаления всех студентов
    """
    try:
        manager = StudentManager(db)
        count = manager.delete_all_students()

        # Инвалидируем кеш после удаления
        cache.delete_pattern("students:*")
        cache.delete_pattern("courses:*")
        cache.delete_pattern("faculties:*")

        return {
            "success": True,
            "message": f"Успешно удалено {count} студентов",
            "count": count
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при удалении студентов: {str(e)}",
            "count": 0
        }