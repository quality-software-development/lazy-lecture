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


# Тест для UserRequest (эквивалент Credentials)
def test_user_request_valid():
    data = {"username": "ValidUser", "password": "StrongPass1!"}
    req = UserRequest(**data)
    assert req.username == "ValidUser"
    assert req.password == "StrongPass1!"


# Тест для UserCreate – проверка работы валидатора, который должен заменить пароль на его хэш.
def test_user_create_validator(monkeypatch):
    raw_password = "StrongPass1!"
    data = {"username": "ValidUser", "password": raw_password}

    # Патчим не source.app.auth.utils.get_password_hash, а имя, импортированное в users.schemas
    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    user_create = UserCreate(**data)
    # Проверяем, что поле password преобразовано в наш "фейковый" хэш
    assert user_create.password == f"hashed_{raw_password}"
    # Проверяем, что password_timestamp установлен
    assert user_create.password_timestamp > 0


# Тест для UserResponse – поскольку ResponseSchema требует поле id, добавляем его
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


# Тест для UserUpdate – если password задан, то после валидатора он должен быть захеширован
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


# Тест для пагинационных моделей: UserPagination
def test_user_pagination_defaults():
    pagination = UserPagination()
    assert pagination.sort == "id"
    assert pagination.order == "asc"


# Тест для UserPage – проверяем, что список пользователей корректно создаётся.
def test_user_page():
    now = datetime.now(timezone.utc)
    user_resp = {
        "id": 10,
        "username": "UserTest",  # проходит валидацию (только буквы)
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


# Тест для UserId и Username
def test_userid_and_username():
    uid = UserId(user_id=42)
    assert uid.user_id == 42

    uname = Username(username="TestUser")
    assert uname.username == "TestUser"
