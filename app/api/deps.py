from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.services.jwt import decode_access_token


# HTTPBearer - схема безопасности для извлечения токена из заголовка Authorization
# автоматически парсит заголовок "Authorization: Bearer <token>"
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего аутентифицированного пользователя.

    Как это работает:
    1. HTTPBearer автоматически извлекает токен из заголовка Authorization
    2. Декодируем токен и получаем payload (user_id, email)
    3. Ищем пользователя в БД по user_id
    4. Возвращаем объект User

    Использование в роутере:
        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Args:
        credentials: Токен из заголовка Authorization (извлекается автоматически)
        db: Сессия базы данных

    Returns:
        User: Объект пользователя

    Raises:
        HTTPException 401: Если токен невалидный или пользователь не найден
    """

    # Извлекаем сам токен из credentials
    token = credentials.credentials

    # Декодируем токен
    payload = decode_access_token(token)

    # Если токен невалидный или истёк
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный или истёкший токен',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Извлекаем user_id из payload
    user_id: int | None = payload.get('user_id')

    # Если user_id нет в токене
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен: отсутствует user_id',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Ищем пользователя в БД
    user = db.query(User).filter(User.id == user_id).first()

    # Если пользователь не найден (удалён из БД?)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency для получения текущего АКТИВНОГО пользователя.

    Дополнительно проверяет, что аккаунт не деактивирован.
    Использует get_current_user внутри (композиция dependencies).

    Использование в роутере:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_active_user)):
            return {"message": f"Hello, {user.email}!"}

    Args:
        current_user: Пользователь из get_current_user

    Returns:
        User: Активный пользователь

    Raises:
        HTTPException 403: Если аккаунт деактивирован
    """

    # Проверяем, активен ли пользователь
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Аккаунт деактивирован',
        )

    return current_user
