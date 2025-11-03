from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False, comment='Фамилия')
    first_name = Column(String(50), nullable=False, comment='Имя')
    faculty = Column(String(50), nullable=False, comment='Факультет')
    course = Column(String(100), nullable=False, comment='Курс')
    grade = Column(Integer, nullable=False, comment='Оценка')

    def __repr__(self):
        return f"<Student({self.last_name} {self.first_name}, {self.faculty}, {self.course}: {self.grade})>"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment='Имя пользователя')
    email = Column(String(100), unique=True, nullable=False, comment='Email')
    hashed_password = Column(String(255), nullable=False, comment='Хеш пароля')
    is_active = Column(Boolean, default=True, comment='Активен ли пользователь')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='Дата создания')

    def __repr__(self):
        return f"<User({self.username}, {self.email})>"


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment='ID пользователя')
    session_token = Column(String(255), unique=True, nullable=False, comment='Токен сессии')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='Дата создания')
    expires_at = Column(DateTime(timezone=True), nullable=False, comment='Дата истечения')
    is_active = Column(Boolean, default=True, comment='Активна ли сессия')

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, active={self.is_active})>"