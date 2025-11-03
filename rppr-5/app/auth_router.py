from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from .database import get_db
from .auth import AuthService
from .schemas import UserCreate, UserLogin, TokenResponse, UserResponse, LogoutResponse
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем или email уже существует"
        )

    return user


@router.post("/login", response_model=TokenResponse)
def login(
        login_data: UserLogin,
        db: Session = Depends(get_db)
):
    """
    Вход пользователя в систему
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    session_token = auth_service.create_session(user.id)

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании сессии"
        )

    return TokenResponse(
        access_token=session_token,
        user_id=user.id,
        username=user.username
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(
        current_user: UserResponse = Depends(get_current_user),
        authorization: str = Header(...),
        db: Session = Depends(get_db)
):
    """
    Выход пользователя из системы
    """
    try:
        scheme, session_token = authorization.split()
        auth_service = AuthService(db)
        success = auth_service.logout_user(session_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сессия не найдена"
            )

        return LogoutResponse(message="Успешный выход из системы")

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат заголовка авторизации"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе
    """
    return current_user