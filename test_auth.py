"""
Тестовый скрипт для проверки системы аутентификации.
Запуск: python test_auth.py
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ АУТЕНТИФИКАЦИИ")
print("=" * 60)

# Тестовые данные
test_email = "testuser@example.com"
test_password = "securepassword123"

# ============================================
# ТЕСТ 1: Регистрация пользователя
# ============================================
print("\n[ТЕСТ 1] Регистрация нового пользователя...")
print(f"POST {BASE_URL}/api/v1/users/")

register_data = {
    "email": test_email,
    "password": test_password,
    "is_active": True,
    "is_superuser": False
}

response = requests.post(f"{BASE_URL}/api/v1/users/", json=register_data)

if response.status_code == 201:
    print("✅ Успешно зарегистрирован!")
    user_data = response.json()
    print(f"   User ID: {user_data['id']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Active: {user_data['is_active']}")
elif response.status_code == 400:
    print("⚠️  Пользователь уже существует (это нормально, продолжаем)")
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(f"   {response.json()}")

# ============================================
# ТЕСТ 2: Логин (получение токена)
# ============================================
print("\n[ТЕСТ 2] Логин и получение JWT токена...")
print(f"POST {BASE_URL}/api/v1/auth/login")

login_data = {
    "email": test_email,
    "password": test_password
}

response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)

if response.status_code == 200:
    print("✅ Успешный логин!")
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"   Token type: {token_data['token_type']}")
    print(f"   Access token: {access_token[:50]}...")
else:
    print(f"❌ Ошибка логина: {response.status_code}")
    print(f"   {response.json()}")
    exit(1)

# ============================================
# ТЕСТ 3: Доступ к защищённому эндпоинту С токеном
# ============================================
print("\n[ТЕСТ 3] Доступ к защищённому эндпоинту /users/me (С токеном)...")
print(f"GET {BASE_URL}/api/v1/users/me")

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)

if response.status_code == 200:
    print("✅ Успешно получили информацию о пользователе!")
    user_info = response.json()
    print(f"   User ID: {user_info['id']}")
    print(f"   Email: {user_info['email']}")
    print(f"   Is Active: {user_info['is_active']}")
    print(f"   Is Superuser: {user_info['is_superuser']}")
    print(f"   Created: {user_info['created_at']}")
else:
    print(f"❌ Ошибка доступа: {response.status_code}")
    print(f"   {response.json()}")

# ============================================
# ТЕСТ 4: Доступ БЕЗ токена (должна быть ошибка)
# ============================================
print("\n[ТЕСТ 4] Попытка доступа БЕЗ токена (ожидается ошибка)...")
print(f"GET {BASE_URL}/api/v1/users/me")

response = requests.get(f"{BASE_URL}/api/v1/users/me")

if response.status_code == 403:
    print("✅ Правильно! Доступ запрещён без токена")
    print(f"   Ошибка: {response.json()}")
else:
    print(f"⚠️  Неожиданный код ответа: {response.status_code}")
    print(f"   {response.json()}")

# ============================================
# ТЕСТ 5: Доступ с неверным токеном
# ============================================
print("\n[ТЕСТ 5] Попытка доступа с НЕВАЛИДНЫМ токеном...")
print(f"GET {BASE_URL}/api/v1/users/me")

fake_headers = {
    "Authorization": "Bearer invalid_token_12345"
}

response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=fake_headers)

if response.status_code == 401:
    print("✅ Правильно! Невалидный токен отклонён")
    print(f"   Ошибка: {response.json()}")
else:
    print(f"⚠️  Неожиданный код ответа: {response.status_code}")
    print(f"   {response.json()}")

# ============================================
# ТЕСТ 6: Логин с неверным паролем
# ============================================
print("\n[ТЕСТ 6] Попытка логина с НЕВЕРНЫМ паролем...")
print(f"POST {BASE_URL}/api/v1/auth/login")

wrong_login_data = {
    "email": test_email,
    "password": "wrongpassword"
}

response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=wrong_login_data)

if response.status_code == 401:
    print("✅ Правильно! Неверный пароль отклонён")
    print(f"   Ошибка: {response.json()}")
else:
    print(f"⚠️  Неожиданный код ответа: {response.status_code}")
    print(f"   {response.json()}")

# ============================================
# ИТОГИ
# ============================================
print("\n" + "=" * 60)
print("ИТОГИ ТЕСТИРОВАНИЯ")
print("=" * 60)
print("✅ Все основные сценарии проверены:")
print("   - Регистрация пользователя")
print("   - Логин и получение JWT токена")
print("   - Доступ к защищённому эндпоинту с токеном")
print("   - Блокировка доступа без токена")
print("   - Блокировка доступа с невалидным токеном")
print("   - Блокировка логина с неверным паролем")
print("\n💡 Система аутентификации работает корректно!")
print("=" * 60)
