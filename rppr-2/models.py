from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
import re
from typing import Optional


class AppealCreate(BaseModel):
    last_name: str
    first_name: str
    birth_date: date
    phone_number: str
    email: EmailStr

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Фамилия не может быть пустой')

        v = v.strip()

        # Проверка на кириллицу и заглавную первую букву
        if not re.match(r'^[А-ЯЁ][а-яё]*$', v):
            raise ValueError('Фамилия должна начинаться с заглавной буквы и содержать только кириллические символы')

        return v

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым')

        v = v.strip()

        # Проверка на кириллицу и заглавную первую букву
        if not re.match(r'^[А-ЯЁ][а-яё]*$', v):
            raise ValueError('Имя должно начинаться с заглавной буквы и содержать только кириллические символы')

        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Номер телефона не может быть пустым')

        v = v.strip()

        # Простая валидация номера телефона
        # Можно настроить под конкретный формат
        phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Некорректный формат номера телефона')

        return v