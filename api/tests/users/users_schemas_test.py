from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from source.app.users.schemas import (
    UserRequest,
    UserCreate,
    UserResponse,
    UserUpdateRequest,
    UserUpdate,
    UserPage,
    UserPagination,
    UserId,
    Username,
)
from source.app.users.enums import Roles


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректные данные для UserRequest (эквивалент Credentials)
def test_user_request_valid():
    data = {"username": "ValidUser", "password": "StrongPass1!"}
    req = UserRequest(**data)
    assert req.username == "ValidUser"
    assert req.password == "StrongPass1!"


# Техника тест-дизайна: #3 Причинно-следственный анализ
# Автор: Юлиана Мирочнук
# Классы:
# - Проверка работы валидатора в UserCreate, преобразующего пароль
def test_user_create_validator(monkeypatch):
    raw_password = "StrongPass1!"
    data = {"username": "ValidUser", "password": raw_password}

    # Патчим функцию хеширования (fake), чтобы отследить преобразование
    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    user_create = UserCreate(**data)
    assert user_create.password == f"hashed_{raw_password}"
    # Техника тест-дизайна: #2 Граничные значения
    # Проверяем, что временная метка пароля установлена (больше нуля)
    assert user_create.password_timestamp > 0


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректное создание UserResponse с обязательными полями
def test_user_response():
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "username": "ValidUser",
        "active": True,
        "can_interact": False,
        "role": Roles.USER,
        "create_date": now,
        "update_date": now,
    }
    response = UserResponse(**data)
    assert response.username == "ValidUser"
    assert response.active is True
    assert response.can_interact is False
    assert response.role == Roles.USER
    assert response.create_date == now
    assert response.update_date == now


# Техника тест-дизайна: #3 Причинно-следственный анализ
# Автор: Юлиана Мирочнук
# Классы:
# - Проверка работы валидатора в UserUpdate: при наличии пароля он должен быть захеширован
def test_user_update(monkeypatch):
    raw_password = "NewStrongPass1!"
    data = {"password": raw_password, "can_interact": True}

    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    update_req = UserUpdate(**data)
    assert update_req.password == f"hashed_{raw_password}"
    assert update_req.password_timestamp is not None
    assert update_req.can_interact is True


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Типовой сценарий для пагинационных настроек
def test_user_pagination_defaults():
    pagination = UserPagination()
    assert pagination.sort == "id"
    assert pagination.order == "asc"


# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирочнук
# Классы:
# - Проверка создания UserPage с корректным списком пользователей
def test_user_page():
    now = datetime.now(timezone.utc)
    user_resp = {
        "id": 10,
        "username": "UserTest",  # корректное значение
        "active": True,
        "can_interact": True,
        "role": Roles.USER,
        "create_date": now,
        "update_date": now,
    }
    page_data = {
        "users": [user_resp],
        "page": 1,
        "size": 10,
        "total": 1,
        "pages": 1,
    }
    page = UserPage(**page_data)
    assert isinstance(page.users, list)
    assert page.users[0].id == 10
    assert page.users[0].username == "UserTest"


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректное создание моделей UserId и Username
def test_userid_and_username():
    uid = UserId(user_id=42)
    assert uid.user_id == 42

    uname = Username(username="TestUser")
    assert uname.username == "TestUser"
