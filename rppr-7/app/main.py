from database import create_tables, SessionLocal
from crud import StudentManager
import uvicorn


def initialize_database():
    """Инициализация базы данных с тестовыми данными"""
    create_tables()

    db = SessionLocal()
    try:
        manager = StudentManager(db)

        # Проверяем, есть ли уже данные
        existing_students = manager.get_all_students()
        if not existing_students:
            # Загружаем данные из CSV или добавляем тестовые
            count = manager.load_from_csv("students.csv")
            if count == 0:
                # Добавляем тестовые данные
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
                print("Добавлены тестовые данные")
            else:
                print(f"Загружено {count} записей из CSV")
        else:
            print(f"В базе уже есть {len(existing_students)} записей")

    finally:
        db.close()


if __name__ == "__main__":
    # Инициализируем базу данных
    initialize_database()

    # Запускаем FastAPI приложение
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)