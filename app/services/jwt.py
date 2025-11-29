from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT access token.

    Args:
        data: Данные для помещения в токен (обычно user_id и email)

    Returns:
        Зашифрованный JWT токен (строка)

    Как это работает:
    1. Копируем входные данные (чтобы не изменять оригинал)
    2. Добавляем время истечения токена (exp)
    3. Шифруем данные с помощью SECRET_KEY
    4. Возвращаем зашифрованную строку
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({'exp': expire})

    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encode_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Расшифровывает JWT токен и возвращает данные.

    Args:
        token: JWT токен (строка)

    Returns:
        Словарь с данными из токена или None если токен невалидный

    Как это работает:
    1. Пытаемся расшифровать токен используя SECRET_KEY
    2. Если токен валидный - возвращаем данные
    3. Если токен истёк или невалидный - возвращаем None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
