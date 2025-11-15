from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .auth import AuthService


def get_current_user(
        authorization: Optional[str] = Header(None),
        db: Session = Depends(get_db)
):
    """Зависимость для получения текущего пользователя"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )

    try:
        # Формат: Bearer <session_token>
        scheme, session_token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверная схема авторизации"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат заголовка авторизации"
        )

    auth_service = AuthService(db)
    user = auth_service.get_user_by_session_token(session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )

    return user