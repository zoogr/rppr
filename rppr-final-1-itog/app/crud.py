from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, select
from .models import Student
import csv
from typing import List, Optional


class StudentManager:
    def __init__(self, db: Session):
        self.db = db

    # CREATE operations
    def create_student(self, student_data: dict) -> Student:
        """Создание нового студента"""
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
        for student in students:
            self.db.refresh(student)
        return students

    # READ operations
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

    # UPDATE operations
    def update_student(self, student_id: int, student_data) -> Optional[Student]:
        """Обновление данных студента"""
        student = self.get_student_by_id(student_id)
        if not student:
            return None

        update_data = student_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(student, field, value)

        self.db.commit()
        self.db.refresh(student)
        return student

    # DELETE operations
    def delete_student(self, student_id: int) -> bool:
        """Удаление студента по ID"""
        student = self.get_student_by_id(student_id)
        if not student:
            return False

        self.db.delete(student)
        self.db.commit()
        return True

    def delete_all_students(self) -> int:
        """Удаление всех студентов"""
        stmt = select(Student)
        students = self.db.scalars(stmt).all()
        count = len(students)

        for student in students:
            self.db.delete(student)

        self.db.commit()
        return count

    # CSV operations
    def load_from_csv(self, csv_file_path: str) -> int:
        """
        Заполнение модели данными из CSV файла
        """
        students_data = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                for row_num, row in enumerate(csv_reader, 1):
                    try:
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