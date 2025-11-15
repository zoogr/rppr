import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import bcrypt

from .models import User, UserSession
from .schemas import UserCreate

# Настройки аутентификации
SESSION_TOKEN_LENGTH = 32
SESSION_DURATION_DAYS = 7


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def generate_session_token(self) -> str:
        """Генерация токена сессии"""
        return secrets.token_hex(SESSION_TOKEN_LENGTH)

    def register_user(self, user_data: UserCreate) -> Optional[User]:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь с таким username или email
        stmt = select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
        existing_user = self.db.scalar(stmt)

        if existing_user:
            return None

        # Создаем нового пользователя
        hashed_password = self.hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        stmt = select(User).where(User.username == username)
        user = self.db.scalar(stmt)

        if not user or not user.is_active:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user

    def create_session(self, user_id: int) -> Optional[str]:
        """Создание сессии для пользователя"""
        # Деактивируем старые сессии пользователя
        stmt = select(UserSession).where(
            (UserSession.user_id == user_id) &
            (UserSession.is_active == True)
        )
        active_sessions = self.db.scalars(stmt).all()

        for session in active_sessions:
            session.is_active = False

        # Создаем новую сессию
        session_token = self.generate_session_token()
        expires_at = datetime.now() + timedelta(days=SESSION_DURATION_DAYS)

        new_session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )

        self.db.add(new_session)
        self.db.commit()

        return session_token

    def get_user_by_session_token(self, session_token: str) -> Optional[User]:
        """Получение пользователя по токену сессии"""
        stmt = select(UserSession).where(
            (UserSession.session_token == session_token) &
            (UserSession.is_active == True) &
            (UserSession.expires_at > datetime.now())
        )
        session = self.db.scalar(stmt)

        if not session:
            return None

        # Обновляем время истечения сессии
        session.expires_at = datetime.now() + timedelta(days=SESSION_DURATION_DAYS)
        self.db.commit()

        # Возвращаем пользователя
        user_stmt = select(User).where(User.id == session.user_id)
        return self.db.scalar(user_stmt)

    def logout_user(self, session_token: str) -> bool:
        """Выход пользователя (завершение сессии)"""
        stmt = select(UserSession).where(UserSession.session_token == session_token)
        session = self.db.scalar(stmt)

        if not session:
            return False

        session.is_active = False
        self.db.commit()
        return True

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)