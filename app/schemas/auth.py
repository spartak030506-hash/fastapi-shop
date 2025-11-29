from pydantic import BaseModel, EmailStr


# Схема для запроса логина.
# Клиент отправляет email и пароль.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Схема ответа с JWT токеном.
# Возвращается после успешного логина.
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


# Данные, которые хранятся внутри JWT токена (payload).
# После декодирования токена мы получаем эти данные.
class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None

