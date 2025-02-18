from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from source.app.auth.enums import TokenType

# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирончук
# Описание:
#   - Импорт тестируемых функций из auth/services.py.
from source.app.auth.services import (
    validate_user,
    authenticate_user,
    authenticate_token,
    generate_token,
    decode_token,
    authenticate_access_token,
    authenticate_refresh_token,
    authenticate,
    auth,
    auth_admin,
    auth_can_interact,
)
from source.app.users.enums import Roles
from source.app.users.models import User


# Вспомогательная функция для создания фиктивного активного пользователя
def dummy_active_user():
    user = User()
    user.id = 1
    user.active = True
    user.password = "hashed_password"
    user.password_timestamp = 1234567890.0
    user.role = Roles.USER
    user.can_interact = True
    return user


# ============================
# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции validate_user: проверка активного и неактивного пользователя.
# ============================
@pytest.mark.asyncio
async def test_validate_user_active():
    user = dummy_active_user()
    result = await validate_user(user)
    assert result == user


@pytest.mark.asyncio
async def test_validate_user_inactive():
    user = dummy_active_user()
    user.active = False
    with pytest.raises(HTTPException) as exc_info:
        await validate_user(user)
    assert "Your account is blocked" in exc_info.value.detail


# ============================
# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции authenticate_user: сценарии успешной аутентификации,
#     пользователь не найден, неверный пароль и неактивный пользователь.
# ============================
@pytest.mark.asyncio
async def test_authenticate_user_success(monkeypatch):
    user = dummy_active_user()
    fake_db = AsyncMock()
    fake_db.scalar.return_value = user

    monkeypatch.setattr("source.app.auth.services.verify_password", lambda plain_password, hashed_password: True)
    # Используем реальное поведение validate_user

    result = await authenticate_user("testuser", "correct_password", fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    fake_db = AsyncMock()
    fake_db.scalar.return_value = None
    result = await authenticate_user("nonexistent", "any_password", fake_db)
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(monkeypatch):
    user = dummy_active_user()
    fake_db = AsyncMock()
    fake_db.scalar.return_value = user
    monkeypatch.setattr("source.app.auth.services.verify_password", lambda plain_password, hashed_password: False)
    result = await authenticate_user("testuser", "wrong_password", fake_db)
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_inactive(monkeypatch):
    user = dummy_active_user()
    user.active = False
    fake_db = AsyncMock()
    fake_db.scalar.return_value = user
    monkeypatch.setattr("source.app.auth.services.verify_password", lambda plain_password, hashed_password: True)
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("testuser", "correct_password", fake_db)
    assert "Your account is blocked" in exc_info.value.detail


# ============================
# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции authenticate_token: успешное совпадение timestamp, несовпадение,
#     пользователь не найден и неактивный.
# ============================
@pytest.mark.asyncio
async def test_authenticate_token_success():
    user = dummy_active_user()
    fake_db = AsyncMock()
    fake_db.get.return_value = user
    result = await authenticate_token(user_id=1, password_timestamp=1234567890.0, db=fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_authenticate_token_timestamp_mismatch():
    user = dummy_active_user()
    fake_db = AsyncMock()
    fake_db.get.return_value = user
    result = await authenticate_token(user_id=1, password_timestamp=9999999.0, db=fake_db)
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_token_user_not_found():
    fake_db = AsyncMock()
    fake_db.get.return_value = None
    result = await authenticate_token(user_id=1, password_timestamp=1234567890.0, db=fake_db)
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_token_inactive():
    user = dummy_active_user()
    user.active = False
    fake_db = AsyncMock()
    fake_db.get.return_value = user
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_token(user_id=1, password_timestamp=user.password_timestamp, db=fake_db)
    assert "Your account is blocked" in exc_info.value.detail


# ============================
# Техника тест-дизайна: #3 Причинно-следственный анализ
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции generate_token: проверка формирования словаря с access_token и refresh_token.
# ============================
@pytest.mark.asyncio
async def test_generate_token(monkeypatch):
    def fake_jwt_encode(payload, key, algorithm):
        return f"encoded_{payload['token_type']}_{payload['user_id']}"

    monkeypatch.setattr("source.app.auth.services.jwt.encode", fake_jwt_encode)

    token_dict = await generate_token(user_id=1, password_timestamp=1234567890.0)
    assert "access_token" in token_dict
    assert "refresh_token" in token_dict
    assert token_dict["access_token"] == "encoded_access_1"
    assert token_dict["refresh_token"] == "encoded_refresh_1"


# ============================
# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции decode_token: корректное декодирование и обработка исключения.
# ============================
@pytest.mark.asyncio
async def test_decode_token_valid(monkeypatch):
    payload = {"user_id": 1, "token_type": "access", "password_timestamp": 1234567890.0}

    # Здесь патчим jwt.decode (синхронная функция)
    def fake_decode(token, key, algorithms):
        return payload

    monkeypatch.setattr("source.app.auth.services.jwt.decode", fake_decode)
    result = await decode_token("dummy_token")
    assert result == payload


@pytest.mark.asyncio
async def test_decode_token_exception(monkeypatch):
    def fake_decode(token, key, algorithms):
        raise JWTError("error")

    monkeypatch.setattr("source.app.auth.services.jwt.decode", fake_decode)
    result = await decode_token("dummy_token")
    assert result == {}


# ============================
# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции authenticate_access_token: проверка успешного сценария,
#     ошибки по роли, can_interact и некорректного payload.
# ============================
@pytest.mark.asyncio
async def test_authenticate_access_token_success(monkeypatch):
    payload = {"user_id": 1, "token_type": TokenType.ACCESS, "password_timestamp": 1234567890.0}

    async def fake_decode(token):
        return payload

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    user = dummy_active_user()
    fake_db = AsyncMock()

    async def fake_authenticate_token(user_id, password_timestamp, db):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate_token", fake_authenticate_token)
    result = await authenticate_access_token("dummy_token", fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_authenticate_access_token_wrong_role(monkeypatch):
    payload = {"user_id": 1, "token_type": TokenType.ACCESS, "password_timestamp": 1234567890.0}

    async def fake_decode(token):
        return payload

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    user = dummy_active_user()
    user.role = Roles.USER  # Требуется роль "admin"
    fake_db = AsyncMock()

    async def fake_authenticate_token(user_id, password_timestamp, db):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate_token", fake_authenticate_token)
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_access_token("dummy_token", fake_db, roles=["admin"])
    assert "Access restricted" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_access_token_wrong_can_interact(monkeypatch):
    payload = {"user_id": 1, "token_type": TokenType.ACCESS, "password_timestamp": 1234567890.0}

    async def fake_decode(token):
        return payload

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    user = dummy_active_user()
    user.can_interact = False
    fake_db = AsyncMock()

    async def fake_authenticate_token(user_id, password_timestamp, db):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate_token", fake_authenticate_token)
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_access_token("dummy_token", fake_db, can_interact=True)
    assert "Access restricted" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_access_token_invalid_payload(monkeypatch):
    async def fake_decode(token):
        return {}

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    fake_db = AsyncMock()
    result = await authenticate_access_token("dummy_token", fake_db)
    assert result is None


# ============================
# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции authenticate_refresh_token: успешный сценарий и неверный тип токена.
# ============================
@pytest.mark.asyncio
async def test_authenticate_refresh_token_success(monkeypatch):
    payload = {"user_id": 1, "token_type": TokenType.REFRESH, "password_timestamp": 1234567890.0}

    async def fake_decode(token):
        return payload

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    user = dummy_active_user()
    fake_db = AsyncMock()

    async def fake_authenticate_token(user_id, password_timestamp, db):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate_token", fake_authenticate_token)

    async def fake_generate_token(user_id, password_timestamp):
        return {"access_token": "new_access", "refresh_token": "new_refresh"}

    monkeypatch.setattr("source.app.auth.services.generate_token", fake_generate_token)
    result = await authenticate_refresh_token("dummy_token", fake_db)
    assert result == {"access_token": "new_access", "refresh_token": "new_refresh"}


@pytest.mark.asyncio
async def test_authenticate_refresh_token_invalid(monkeypatch):
    payload = {"user_id": 1, "token_type": "access", "password_timestamp": 1234567890.0}

    async def fake_decode(token):
        return payload

    monkeypatch.setattr("source.app.auth.services.decode_token", fake_decode)
    fake_db = AsyncMock()
    result = await authenticate_refresh_token("dummy_token", fake_db)
    assert result is None


# ============================
# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функции authenticate: успешная аутентификация и неудача с вызовом unauthorized.
# ============================
@pytest.mark.asyncio
async def test_authenticate_success(monkeypatch):
    user = dummy_active_user()

    async def fake_authenticate_access_token(token, db, roles=None, can_interact=None):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate_access_token", fake_authenticate_access_token)
    fake_db = AsyncMock()
    result = await authenticate("dummy_token", fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_authenticate_failure(monkeypatch):
    async def fake_authenticate_access_token(token, db, roles=None, can_interact=None):
        return None

    monkeypatch.setattr("source.app.auth.services.authenticate_access_token", fake_authenticate_access_token)
    fake_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await authenticate("dummy_token", fake_db)
    assert "Invalid or expired token" in exc_info.value.detail


# ============================
# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тесты для функций auth, auth_admin и auth_can_interact: проверка сценариев с отсутствующим токеном и корректным токеном.
# ============================
@pytest.mark.asyncio
async def test_auth_no_token(monkeypatch):
    fake_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await auth(token=None, db=fake_db)
    assert "Invalid Authorization Header" in exc_info.value.detail


@pytest.mark.asyncio
async def test_auth_valid(monkeypatch):
    user = dummy_active_user()
    fake_db = AsyncMock()

    async def fake_authenticate(token, db, roles=None, can_interact=None):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate", fake_authenticate)
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="dummy_token")
    result = await auth(token=token, db=fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_auth_admin_no_token(monkeypatch):
    fake_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await auth_admin(token=None, db=fake_db)
    assert "Invalid Authorization Header" in exc_info.value.detail


@pytest.mark.asyncio
async def test_auth_admin_valid(monkeypatch):
    user = dummy_active_user()
    fake_db = AsyncMock()

    async def fake_authenticate(token, db, roles=None, can_interact=None):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate", fake_authenticate)
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="dummy_token")
    result = await auth_admin(token=token, db=fake_db)
    assert result == user


@pytest.mark.asyncio
async def test_auth_can_interact_no_token(monkeypatch):
    fake_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await auth_can_interact(token=None, db=fake_db)
    assert "Invalid Authorization Header" in exc_info.value.detail


@pytest.mark.asyncio
async def test_auth_can_interact_valid(monkeypatch):
    user = dummy_active_user()
    fake_db = AsyncMock()

    async def fake_authenticate(token, db, roles=None, can_interact=None):
        return user

    monkeypatch.setattr("source.app.auth.services.authenticate", fake_authenticate)
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="dummy_token")
    result = await auth_can_interact(token=token, db=fake_db)
    assert result == user
