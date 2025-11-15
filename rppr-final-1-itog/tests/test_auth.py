import pytest
from fastapi import status


class TestAuthEndpoints:
    """Тесты для эндпоинтов аутентификации"""

    def test_register_success(self, client):
        """Тест успешной регистрации пользователя"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }

        # Act
        response = client.post("/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data  # Пароль не должен возвращаться

    def test_register_duplicate_username(self, client):
        """Тест регистрации с существующим username"""
        # Arrange
        user_data = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "password123"
        }

        # Создаем первого пользователя
        client.post("/auth/register", json=user_data)

        # Пытаемся создать второго с тем же username
        duplicate_data = {
            "username": "duplicateuser",
            "email": "user2@example.com",
            "password": "differentpassword"
        }

        # Act
        response = client.post("/auth/register", json=duplicate_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Тест регистрации с некорректным email"""
        # Arrange
        invalid_user_data = {
            "username": "validuser",
            "email": "invalid-email",
            "password": "password123"
        }

        # Act
        response = client.post("/auth/register", json=invalid_user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client):
        """Тест успешного входа в систему"""
        # Arrange
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpassword123"
        }

        # Регистрируем пользователя
        client.post("/auth/register", json=user_data)

        login_data = {
            "username": "loginuser",
            "password": "loginpassword123"
        }

        # Act
        response = client.post("/auth/login", json=login_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == user_data["username"]
        assert "user_id" in data

    def test_login_wrong_password(self, client):
        """Тест входа с неправильным паролем"""
        # Arrange
        user_data = {
            "username": "loginuser2",
            "email": "login2@example.com",
            "password": "correctpassword"
        }

        # Регистрируем пользователя
        client.post("/auth/register", json=user_data)

        wrong_login_data = {
            "username": "loginuser2",
            "password": "wrongpassword"
        }

        # Act
        response = client.post("/auth/login", json=wrong_login_data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "неверное" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        # Arrange
        login_data = {
            "username": "nonexistent",
            "password": "anypassword"
        }

        # Act
        response = client.post("/auth/login", json=login_data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_success(self, client, auth_headers):
        """Тест успешного получения информации о текущем пользователе"""
        # Act
        response = client.get("/auth/me", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data

    def test_get_current_user_unauthorized(self, client):
        """Тест получения информации о пользователе без авторизации"""
        # Act
        response = client.get("/auth/me")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_success(self, client, auth_headers):
        """Тест успешного выхода из системы"""
        # Act
        response = client.post("/auth/logout", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "успешный выход" in response.json()["message"].lower()

    def test_logout_invalid_token(self, client):
        """Тест выхода с невалидным токеном"""
        # Arrange
        invalid_headers = {"Authorization": "Bearer invalid_token"}

        # Act
        response = client.post("/auth/logout", headers=invalid_headers)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED