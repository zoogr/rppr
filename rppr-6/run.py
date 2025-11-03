from app.database import create_tables, SessionLocal
from app.auth import AuthService
from app.schemas import UserCreate
import uvicorn
import subprocess
import sys
import time


def check_redis_connection():
    """Проверка подключения к Redis"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis подключен успешно")
        return True
    except redis.ConnectionError:
        print("❌ Redis не доступен. Запустите Redis сервер:")
        print("   sudo service redis-server start  # Linux")
        print("   brew services start redis        # macOS")
        print("   redis-server                    # Windows")
        return False


def initialize_database():
    """Инициализация базы данных с тестовыми данными"""
    create_tables()

    db = SessionLocal()
    try:
        # Создаем тестового пользователя если его нет
        auth_service = AuthService(db)

        from sqlalchemy import select
        from app.models import User

        stmt = select(User)
        existing_users = db.scalars(stmt).all()

        if not existing_users:
            test_user = UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            auth_service.register_user(test_user)
            print("✅ Создан тестовый пользователь: admin / admin123")

        # Инициализируем тестовые данные студентов
        from app.crud import StudentManager
        manager = StudentManager(db)

        existing_students = manager.get_all_students()
        if not existing_students:
            test_data = [
                {
                    'last_name': 'Ли',
                    'first_name': 'Иван',
                    'faculty': 'АВТФ',
                    'course': 'Теор. Механика',
                    'grade': 52
                },
                {
                    'last_name': 'Ким',
                    'first_name': 'Петр',
                    'faculty': 'ФГМИ',
                    'course': 'Мат. Анализ',
                    'grade': 28
                }
            ]
            manager.insert_multiple_students(test_data)
            print("✅ Добавлены тестовые данные студентов")

    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Запуск Student Management API...")

    # Проверяем Redis
    if not check_redis_connection():
        print("⚠️  Приложение запустится без кеширования")

    # Инициализируем базу данных
    initialize_database()

    # Запускаем FastAPI приложение
    print("🌐 Запуск FastAPI сервера...")
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)