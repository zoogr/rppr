from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, select
from models import Student
import csv
from typing import List, Optional


class StudentManager:
    def __init__(self, db: Session):
        self.db = db

    def insert_student(self, student_data: dict) -> Student:
        """Добавление одного студента в базу данных"""
        student = Student(**student_data)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def insert_multiple_students(self, students_data: List[dict]) -> List[Student]:
        """Добавление нескольких студентов в базу данных"""
        students = [Student(**data) for data in students_data]
        self.db.add_all(students)
        self.db.commit()
        # Обновляем объекты чтобы получить их ID
        for student in students:
            self.db.refresh(student)
        return students

    def get_all_students(self) -> List[Student]:
        """Получение всех студентов"""
        stmt = select(Student)
        return list(self.db.scalars(stmt).all())

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Получение студента по ID"""
        stmt = select(Student).where(Student.id == student_id)
        return self.db.scalar(stmt)

    def get_students_by_faculty(self, faculty: str) -> List[Student]:
        """Получение списка студентов по названию факультета"""
        stmt = select(Student).where(Student.faculty == faculty)
        return list(self.db.scalars(stmt).all())

    def get_unique_courses(self) -> List[str]:
        """Получение списка уникальных курсов"""
        stmt = select(distinct(Student.course))
        courses = self.db.scalars(stmt).all()
        return list(courses)

    def get_average_grade_by_faculty(self, faculty: str) -> float:
        """Получение среднего балла по факультету"""
        stmt = select(func.avg(Student.grade)).where(Student.faculty == faculty)
        result = self.db.scalar(stmt)
        return round(result, 2) if result else 0.0

    def get_all_faculties(self) -> List[str]:
        """Получение списка всех факультетов"""
        stmt = select(distinct(Student.faculty))
        faculties = self.db.scalars(stmt).all()
        return list(faculties)

    def load_from_csv(self, csv_file_path: str) -> int:
        """
        Заполнение модели данными из CSV файла

        Args:
            csv_file_path: путь к CSV файлу

        Returns:
            количество добавленных записей
        """
        students_data = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                for row_num, row in enumerate(csv_reader, 1):
                    try:
                        # Преобразуем данные из CSV в формат модели
                        student_data = {
                            'last_name': row['Фамилия'],
                            'first_name': row['Имя'],
                            'faculty': row['Факультет'],
                            'course': row['Курс'],
                            'grade': int(row['Оценка'])
                        }
                        students_data.append(student_data)
                    except (KeyError, ValueError) as e:
                        print(f"Ошибка в строке {row_num}: {e}")
                        continue

            # Добавляем все данные в базу
            if students_data:
                students = self.insert_multiple_students(students_data)
                return len(students)
            else:
                return 0

        except FileNotFoundError:
            print(f"Файл {csv_file_path} не найден")
            return 0
        except Exception as e:
            print(f"Ошибка при чтении CSV файла: {e}")
            return 0