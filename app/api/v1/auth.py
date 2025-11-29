from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.services.auth import verify_password
from app.services.jwt import create_access_token


router = APIRouter()


@router.post('/login', response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Эндпоинт для логина пользователя.

    Принимает email и пароль, возвращает JWT токен.

    Шаги:
    1. Ищем пользователя по email в базе данных
    2. Проверяем, существует ли пользователь
    3. Проверяем правильность пароля
    4. Проверяем, активен ли аккаунт
    5. Создаём JWT токен с данными пользователя
    6. Возвращаем токен
    """

    # Шаг 1: Ищем пользователя по email
    user = db.query(User).filter(User.email == credentials.email).first()

    # Шаг 2: Проверяем существование пользователя
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный email или пароль',
        )

    # Шаг 3: Проверяем пароль
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный email или пароль',
        )

    # Шаг 4: Проверяем активность аккаунта
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Аккаунт деактивирован',
        )

    # Шаг 5: Создаём JWT токен
    access_token = create_access_token(
        data={
            'user_id': user.id,
            'email': user.email,
        }
    )

    # Шаг 6: Возвращаем токен
    return Token(access_token=access_token, token_type='bearer')
