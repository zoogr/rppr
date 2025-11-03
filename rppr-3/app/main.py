from database import create_tables, SessionLocal
from crud import StudentManager
import os


def main():
    # Создаем таблицы
    create_tables()

    # Создаем сессию базы данных
    db = SessionLocal()

    try:
        # Создаем менеджер студентов
        manager = StudentManager(db)

        # Загружаем данные из CSV файла
        csv_file = "students.csv"
        count = manager.load_from_csv(csv_file)

        if count > 0:
            print(f"Добавлено {count} записей из CSV файла")
        else:
            print(f"Файл {csv_file} не найден или пуст. Добавляем тестовые данные...")
            # Добавим тестовые данные для демонстрации
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
                },
                {
                    'last_name': 'Райт',
                    'first_name': 'Вероника',
                    'faculty': 'ФЛА',
                    'course': 'Теор. Механика',
                    'grade': 7
                },
                {
                    'last_name': 'Джонс',
                    'first_name': 'Андрей',
                    'faculty': 'РЭФ',
                    'course': 'Мат. Анализ',
                    'grade': 4
                },
                {
                    'last_name': 'Джонс',
                    'first_name': 'Андрей',
                    'faculty': 'РЭФ',
                    'course': 'Информатика',
                    'grade': 40
                }
            ]
            manager.insert_multiple_students(test_data)
            print("Добавлены тестовые данные")

        # Демонстрация работы методов
        print("\n" + "=" * 50)
        print("ДЕМОНСТРАЦИЯ РАБОТЫ МЕТОДОВ")
        print("=" * 50)

        print("\n=== Все студенты ===")
        all_students = manager.get_all_students()
        for student in all_students:
            print(f"{student.last_name} {student.first_name} - {student.faculty} - {student.course}: {student.grade}")

        print("\n=== Студенты ФГМИ ===")
        fgmi_students = manager.get_students_by_faculty('ФГМИ')
        for student in fgmi_students:
            print(f"{student.last_name} {student.first_name} - {student.course}: {student.grade}")

        print("\n=== Уникальные курсы ===")
        unique_courses = manager.get_unique_courses()
        for course in unique_courses:
            print(f"• {course}")

        print("\n=== Средние баллы по факультетам ===")
        faculties = manager.get_all_faculties()
        for faculty in faculties:
            avg_grade = manager.get_average_grade_by_faculty(faculty)
            print(f"{faculty}: {avg_grade}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()