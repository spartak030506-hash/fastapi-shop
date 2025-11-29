# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Проект

FastAPI Shop - это веб-приложение для интернет-магазина на основе FastAPI с использованием SQLAlchemy и Alembic для миграций базы данных.

## Установка и запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск сервера разработки
```bash
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`

### Проверка работоспособности
```bash
# Health check эндпоинт
curl http://127.0.0.1:8000/health
```

## База данных и миграции

### Создание новой миграции
```bash
alembic revision --autogenerate -m "описание миграции"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат на одну миграцию назад
```bash
alembic downgrade -1
```

### Просмотр истории миграций
```bash
alembic history
```

## Архитектура проекта

### Структура каталогов
- `app/` - основной код приложения
  - `api/v1/` - API эндпоинты версии 1
  - `core/` - конфигурация и базовые компоненты (настройки, БД)
  - `models/` - SQLAlchemy модели базы данных
  - `schemas/` - Pydantic схемы для валидации и сериализации
  - `services/` - бизнес-логика и вспомогательные сервисы
  - `main.py` - точка входа приложения
- `alembic/` - миграции базы данных
  - `versions/` - файлы миграций
  - `env.py` - конфигурация Alembic

### Конфигурация

Настройки приложения находятся в `app/core/config.py` и используют Pydantic Settings. Конфигурация загружается из файла `.env` в корне проекта.

Основные переменные окружения:
- `DATABASE_URL` - URL подключения к базе данных (по умолчанию SQLite)
- `SECRET_KEY` - секретный ключ для JWT токенов
- `ACCESS_TOKEN_EXPIRE_MINUTES` - время жизни access токенов
- `ALGORITHM` - алгоритм шифрования для JWT

### База данных

Используется SQLAlchemy с поддержкой как SQLite (для разработки), так и других БД (PostgreSQL и т.д.).

- База классов моделей: `app.core.db.Base` (DeclarativeBase из SQLAlchemy)
- Функция получения сессии БД: `app.core.db.get_db()` - используется как dependency в роутерах
- Конфигурация engine учитывает особенности SQLite (`check_same_thread=False`)

### Модели и схемы

При добавлении новых моделей:
1. Создать модель в `app/models/` наследуясь от `Base`
2. Импортировать модель в `app/models/__init__.py`
3. Импортировать модель в `alembic/env.py` (строка 13) для автогенерации миграций
4. Создать соответствующие Pydantic схемы в `app/schemas/`

Существующие модели:
- `User` в `app/models/user.py` - пользователи с полями email, hashed_password, is_active, is_superuser, created_at, updated_at

### API роутеры

Роутеры организованы по версиям API в `app/api/v{version}/`. Каждый роутер подключается в `app/main.py` с соответствующим prefix и tags.

Текущие эндпоинты:
- `/api/v1/users/` - работа с пользователями
- `/health` - проверка здоровья приложения

### Аутентификация

Хеширование паролей реализовано в `app/services/auth.py` с использованием bcrypt напрямую:
- `get_password_hash(password)` - хеширование пароля используя bcrypt
- `verify_password(plain_password, hashed_password)` - проверка пароля

**Важно**: Проект использует `bcrypt>=4.0.0` напрямую, без `passlib`, для совместимости с современными версиями библиотек.

## Особенности разработки

### Важные технические детали

1. **Импорт моделей в Alembic**: При создании новых моделей обязательно добавить импорт в `alembic/env.py` (строка 13), иначе автогенерация миграций не будет работать корректно.

2. **SQLite особенности**: В режиме SQLite используется `check_same_thread=False` для корректной работы с FastAPI.

3. **Pydantic конфигурация**: Схемы для чтения из БД используют `model_config = ConfigDict(from_attributes=True)` для работы с SQLAlchemy моделями.

4. **Timezone aware datetime**: Модель User использует `DateTime(timezone=True)` с автоматическими значениями через `func.now()`.

5. **Версионирование API**: Все эндпоинты организованы по версиям (`/api/v1/`), что позволяет поддерживать несколько версий API одновременно.
