import pytest
from fastapi import status


class TestAdditionalEndpoints:
    """Тесты для дополнительных эндпоинтов"""

    def test_get_students_by_faculty_success(self, client, auth_headers):
        """Тест успешного получения студентов по факультету"""
        # Arrange - создаем студентов разных факультетов
        students_data = [
            {
                "last_name": "ФИТовец",
                "first_name": "Алексей",
                "faculty": "ФИТ",
                "course": "Программирование",
                "grade": 85
            },
            {
                "last_name": "ФГМИшник",
                "first_name": "Мария",
                "faculty": "ФГМИ",
                "course": "Математика",
                "grade": 92
            },
            {
                "last_name": "ФИТовец2",
                "first_name": "Иван",
                "faculty": "ФИТ",
                "course": "Базы данных",
                "grade": 78
            }
        ]

        for student_data in students_data:
            client.post("/students/", json=student_data, headers=auth_headers)

        # Act
        response = client.get("/students/faculty/ФИТ", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 2
        for student in data["students"]:
            assert student["faculty"] == "ФИТ"

    def test_get_students_by_faculty_empty(self, client, auth_headers):
        """Тест получения студентов по несуществующему факультету"""
        # Act
        response = client.get("/students/faculty/НЕСУЩЕСТВУЮЩИЙ", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["students"]) == 0

    def test_get_unique_courses_success(self, client, auth_headers):
        """Тест успешного получения уникальных курсов"""
        # Arrange - создаем студентов с разными курсами
        students_data = [
            {
                "last_name": "Студент1",
                "first_name": "Имя1",
                "faculty": "ФИТ",
                "course": "Программирование",
                "grade": 85
            },
            {
                "last_name": "Студент2",
                "first_name": "Имя2",
                "faculty": "ФИТ",
                "course": "Базы данных",
                "grade": 90
            },
            {
                "last_name": "Студент3",
                "first_name": "Имя3",
                "faculty": "ФГМИ",
                "course": "Программирование",  # Дублирующий курс
                "grade": 88
            }
        ]

        for student_data in students_data:
            client.post("/students/", json=student_data, headers=auth_headers)

        # Act
        response = client.get("/courses/", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "courses" in data
        courses = data["courses"]
        assert "Программирование" in courses
        assert "Базы данных" in courses
        assert len(courses) >= 2  # Должны быть уникальные курсы

    def test_get_average_grade_success(self, client, auth_headers):
        """Тест успешного получения среднего балла по факультету"""
        # Arrange - создаем студентов ФИТ с разными оценками
        fit_students = [
            {"last_name": "ФИТ1", "first_name": "Имя1", "faculty": "ФИТ", "course": "Курс1", "grade": 80},
            {"last_name": "ФИТ2", "first_name": "Имя2", "faculty": "ФИТ", "course": "Курс2", "grade": 90},
            {"last_name": "ФИТ3", "first_name": "Имя3", "faculty": "ФИТ", "course": "Курс3", "grade": 70}
        ]

        for student_data in fit_students:
            client.post("/students/", json=student_data, headers=auth_headers)

        # Создаем студента другого факультета
        other_faculty_student = {
            "last_name": "Другой",
            "first_name": "Факультет",
            "faculty": "ФГМИ",
            "course": "Курс",
            "grade": 100
        }
        client.post("/students/", json=other_faculty_student, headers=auth_headers)

        # Act
        response = client.get("/faculties/ФИТ/average-grade", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["faculty"] == "ФИТ"
        assert "average_grade" in data
        # Среднее от 80, 90, 70 = 80
        assert data["average_grade"] == 80.0

    def test_get_average_grade_empty_faculty(self, client, auth_headers):
        """Тест получения среднего балла по факультету без студентов"""
        # Act
        response = client.get("/faculties/ПУСТОЙ/average-grade", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["faculty"] == "ПУСТОЙ"
        assert data["average_grade"] == 0.0


class TestHealthEndpoints:
    """Тесты для health-check эндпоинтов"""

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self, client):
        """Тест health-check эндпоинта"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "redis" in data