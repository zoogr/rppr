from sqlalchemy import Column, Integer, String
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

    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            'id': self.id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'faculty': self.faculty,
            'course': self.course,
            'grade': self.grade
        }