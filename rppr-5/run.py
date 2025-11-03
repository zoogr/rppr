from app.database import create_tables, SessionLocal
from app.auth import AuthService
from app.schemas import UserCreate
import uvicorn


def initialize_database():
    """Инициализация базы данных с тестовыми данными"""
    create_tables()

    db = SessionLocal()
    try:
        # Создаем тестового пользователя если его нет
        auth_service = AuthService(db)

        # Проверяем, есть ли пользователи
        from sqlalchemy import select
        from app.models import User

        stmt = select(User)
        existing_users = db.scalars(stmt).all()

        if not existing_users:
            # Создаем тестового пользователя
            test_user = UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            auth_service.register_user(test_user)
            print("Создан тестовый пользователь: admin / admin123")

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
            print("Добавлены тестовые данные студентов")

    finally:
        db.close()


if __name__ == "__main__":
    # Инициализируем базу данных
    initialize_database()

    # Запускаем FastAPI приложение
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)