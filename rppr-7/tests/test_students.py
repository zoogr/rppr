import pytest
from fastapi import status


class TestStudentEndpoints:
    """Тесты для эндпоинтов управления студентами"""

    def test_create_student_success(self, client, auth_headers):
        """Тест успешного создания студента"""
        # Arrange
        student_data = {
            "last_name": "Иванов",
            "first_name": "Иван",
            "faculty": "ФИТ",
            "course": "Программирование",
            "grade": 85
        }

        # Act
        response = client.post("/students/", json=student_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["last_name"] == student_data["last_name"]
        assert data["first_name"] == student_data["first_name"]
        assert data["faculty"] == student_data["faculty"]
        assert data["course"] == student_data["course"]
        assert data["grade"] == student_data["grade"]
        assert "id" in data

    def test_create_student_unauthorized(self, client):
        """Тест создания студента без авторизации"""
        # Arrange
        student_data = {
            "last_name": "Иванов",
            "first_name": "Иван",
            "faculty": "ФИТ",
            "course": "Программирование",
            "grade": 85
        }

        # Act
        response = client.post("/students/", json=student_data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_student_invalid_data(self, client, auth_headers):
        """Тест создания студента с некорректными данными"""
        # Arrange
        invalid_student_data = {
            "last_name": "",  # Пустая фамилия
            "first_name": "Иван",
            "faculty": "ФИТ",
            "course": "Программирование",
            "grade": 150  # Оценка больше 100
        }

        # Act
        response = client.post("/students/", json=invalid_student_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_all_students_success(self, client, auth_headers):
        """Тест успешного получения всех студентов"""
        # Arrange - создаем несколько студентов
        students_data = [
            {
                "last_name": "Петров",
                "first_name": "Петр",
                "faculty": "ФИТ",
                "course": "Базы данных",
                "grade": 90
            },
            {
                "last_name": "Сидорова",
                "first_name": "Мария",
                "faculty": "ФГМИ",
                "course": "Математика",
                "grade": 95
            }
        ]

        for student_data in students_data:
            client.post("/students/", json=student_data, headers=auth_headers)

        # Act
        response = client.get("/students/", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "students" in data
        assert len(data["students"]) >= 2

    def test_get_all_students_unauthorized(self, client):
        """Тест получения студентов без авторизации"""
        # Act
        response = client.get("/students/")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_student_by_id_success(self, client, auth_headers):
        """Тест успешного получения студента по ID"""
        # Arrange - создаем студента
        student_data = {
            "last_name": "Кузнецов",
            "first_name": "Алексей",
            "faculty": "РЭФ",
            "course": "Экономика",
            "grade": 88
        }

        create_response = client.post("/students/", json=student_data, headers=auth_headers)
        student_id = create_response.json()["id"]

        # Act
        response = client.get(f"/students/{student_id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == student_id
        assert data["last_name"] == student_data["last_name"]

    def test_get_student_by_id_not_found(self, client, auth_headers):
        """Тест получения несуществующего студента"""
        # Act
        response = client.get("/students/9999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_student_success(self, client, auth_headers):
        """Тест успешного обновления студента"""
        # Arrange - создаем студента
        student_data = {
            "last_name": "Обновляем",
            "first_name": "Студент",
            "faculty": "ФИТ",
            "course": "Программирование",
            "grade": 75
        }

        create_response = client.post("/students/", json=student_data, headers=auth_headers)
        student_id = create_response.json()["id"]

        update_data = {
            "grade": 90,
            "course": "Веб-разработка"
        }

        # Act
        response = client.put(f"/students/{student_id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == student_id
        assert data["grade"] == update_data["grade"]
        assert data["course"] == update_data["course"]
        # Проверяем, что остальные поля не изменились
        assert data["last_name"] == student_data["last_name"]

    def test_update_student_not_found(self, client, auth_headers):
        """Тест обновления несуществующего студента"""
        # Arrange
        update_data = {"grade": 100}

        # Act
        response = client.put("/students/9999", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_student_success(self, client, auth_headers):
        """Тест успешного удаления студента"""
        # Arrange - создаем студента
        student_data = {
            "last_name": "Удаляем",
            "first_name": "Студент",
            "faculty": "ФИТ",
            "course": "Программирование",
            "grade": 80
        }

        create_response = client.post("/students/", json=student_data, headers=auth_headers)
        student_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/students/{student_id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что студент действительно удален
        get_response = client.get(f"/students/{student_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_student_not_found(self, client, auth_headers):
        """Тест удаления несуществующего студента"""
        # Act
        response = client.delete("/students/9999", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND