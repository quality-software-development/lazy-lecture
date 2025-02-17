from datetime import datetime, timezone
from math import ceil
# Для асинхронных тестов используем AsyncMock
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from source.app.users.enums import Sort, Order, Roles
from source.app.users.models import User
from source.app.users.schemas import (
    UserRequest,
    UserUpdateRequest,
    UserResponse,
)
from source.app.users.services import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    list_users,
)


# Фикстура для корректного UserRequest – передаем Pydantic‑модель
@pytest.fixture
def fake_user_request():
    return UserRequest(username="testuser", password="StrongPass1!")


# Фикстура для невалидного UserRequest (например, недопустимый username)
@pytest.fixture
def fake_invalid_user_request():
    # Возвращаем словарь с невалидными данными
    return {"username": "123", "password": "StrongPass1!"}


def fake_user():
    test_user = User()
    test_user.username = "testuser"
    test_user.password = "old_hash"
    test_user.active = True
    test_user.role = "user"
    test_user.can_interact = False
    return test_user


@pytest.fixture
def fake_db_session():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.get_one = AsyncMock()
    db.scalar = AsyncMock()
    db.scalars = MagicMock()
    db.delete = AsyncMock()  # используем AsyncMock, чтобы можно было await
    return db


# =================== Тесты для create_user ===================

@pytest.mark.asyncio
async def test_create_user_success(fake_user_request, fake_db_session, monkeypatch):
    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    # Подменяем get_password_hash там, где она используется в UserCreate
    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    fake_db_session.commit.return_value = None
    fake_db_session.refresh.return_value = None

    created_user = await create_user(user=fake_user_request, db=fake_db_session)
    assert isinstance(created_user, User)
    assert created_user.password == f"hashed_{fake_user_request.password}"


@pytest.mark.asyncio
async def test_create_user_integrity_error(fake_user_request, fake_db_session):
    fake_db_session.commit.side_effect = IntegrityError("dummy", "params", Exception("dummy"))
    result = await create_user(user=fake_user_request, db=fake_db_session)
    assert result is None


# Дополнительный тест: неверный вход (невалидные данные)
@pytest.mark.asyncio
async def test_create_user_invalid_input(fake_invalid_user_request, fake_db_session):
    with pytest.raises(Exception):  # или конкретно ValidationError
        # Попытка создать пользователя с невалидными данными должна вызывать ошибку
        await create_user(user=fake_invalid_user_request, db=fake_db_session)


# =================== Тесты для get_user_by_id ===================

@pytest.mark.asyncio
async def test_get_user_by_id_found(fake_db_session):
    test_user = User()
    test_user.username = "testuser"
    fake_db_session.get_one.return_value = test_user

    user = await get_user_by_id(user_id=1, db=fake_db_session)
    fake_db_session.get_one.assert_called_once_with(User, 1)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(fake_db_session):
    # Если db.get_one возвращает None, функция должна вернуть None
    fake_db_session.get_one.return_value = None
    user = await get_user_by_id(user_id=999, db=fake_db_session)
    assert user is None


# =================== Тесты для update_user ===================

@pytest.mark.asyncio
async def test_update_user_success(fake_db_session, monkeypatch):
    test_user = fake_user()

    update_data = {"password": "NewStrongPass1!", "can_interact": True}
    update_request = UserUpdateRequest(**update_data)

    fake_db_session.commit.return_value = None
    fake_db_session.refresh.return_value = None

    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    updated_user = await update_user(user=test_user, request=update_request, db=fake_db_session)
    assert updated_user.password == f"hashed_{update_data['password']}"
    assert updated_user.can_interact is True


# Дополнительный тест: пустой запрос на обновление (все поля None)
@pytest.mark.asyncio
async def test_update_user_no_changes(fake_db_session):
    # Создаем пользователя с начальными значениями
    test_user = User()
    test_user.username = "testuser"
    test_user.password = "old_hash"
    test_user.active = True
    test_user.role = "user"
    test_user.can_interact = False

    # Передаем пустой запрос: все поля None
    update_data = {}  # Пустой запрос
    update_request = UserUpdateRequest(**update_data)

    fake_db_session.commit.return_value = None
    fake_db_session.refresh.return_value = None

    updated_user = await update_user(user=test_user, request=update_request, db=fake_db_session)
    # Ожидаем, что никаких изменений не произойдет
    assert updated_user.password == "old_hash"
    assert updated_user.can_interact is False


# Дополнительный тест: IntegrityError при обновлении
@pytest.mark.asyncio
async def test_update_user_integrity_error(fake_db_session, monkeypatch):
    test_user = fake_user()

    update_data = {"password": "NewStrongPass1!", "can_interact": True}
    update_request = UserUpdateRequest(**update_data)

    fake_db_session.commit.side_effect = IntegrityError("dummy", "params", Exception("dummy"))

    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    result = await update_user(user=test_user, request=update_request, db=fake_db_session)
    assert result is None


# =================== Тесты для delete_user ===================

@pytest.mark.asyncio
async def test_delete_user_success(fake_db_session):
    test_user = User()
    await delete_user(user=test_user, db=fake_db_session)
    fake_db_session.delete.assert_called_once_with(test_user)
    fake_db_session.commit.assert_called_once()


# Дополнительный тест: исключение при удалении (например, если commit выбрасывает ошибку)
@pytest.mark.asyncio
async def test_delete_user_exception(fake_db_session):
    test_user = User()
    fake_db_session.delete.side_effect = Exception("Delete error")
    with pytest.raises(Exception, match="Delete error"):
        await delete_user(user=test_user, db=fake_db_session)


# =================== Тесты для list_users ===================

@pytest.mark.asyncio
async def test_list_users_success(fake_db_session):
    # Создаем корректно заполненные объекты User
    now = datetime.now(timezone.utc)
    user1 = User(
        id=1,
        username="UserOne",
        active=True,
        can_interact=True,
        role=Roles.USER,
        password_timestamp=123456.0
    )
    user1.create_date = now
    user1.update_date = now

    user2 = User(
        id=2,
        username="UserTwo",
        active=True,
        can_interact=False,
        role=Roles.USER,
        password_timestamp=123456.0
    )
    user2.create_date = now
    user2.update_date = now

    users_list = [user1, user2]

    # Создаем фиктивный объект, который реализует асинхронный метод all() и является awaitable,
    # при await возвращает результат метода all(), то есть users_list.
    class FakeScalars:
        async def all(self):
            return users_list

        def __await__(self):
            return self.all().__await__()

    fake_db_session.scalars.return_value = FakeScalars()
    fake_db_session.scalar.return_value = 2

    page = 1
    size = 10
    sort = Sort.ID
    order = Order.ASC

    user_page = await list_users(page, size, sort, order, db=fake_db_session)
    assert user_page.page == page
    assert user_page.size == size
    assert user_page.total == 2
    assert user_page.pages == ceil(2 / size)
    # Сравниваем представления в виде словарей:
    expected = [UserResponse.from_orm(u).dict() for u in users_list]
    actual = [r.dict() for r in user_page.users]
    assert actual == expected


# Дополнительный тест: пустой результат – нет пользователей
@pytest.mark.asyncio
async def test_list_users_empty(fake_db_session):
    # Если пользователей нет, total = 0, users = []
    class FakeScalars:
        @staticmethod
        async def all():
            return []

        def __await__(self):
            return self.all().__await__()

    fake_db_session.scalars.return_value = FakeScalars()
    fake_db_session.scalar.return_value = 0

    page = 1
    size = 10
    sort = Sort.ID
    order = Order.ASC

    user_page = await list_users(page, size, sort, order, db=fake_db_session)
    assert user_page.page == page
    assert user_page.size == size
    assert user_page.total == 0
    # В зависимости от логики, pages может быть 0 или 1; предположим, что 0
    assert user_page.pages == 0
    assert user_page.users == []


# Дополнительный тест: исключение при подсчете общего количества (db.scalar выбрасывает ошибку)
@pytest.mark.asyncio
async def test_list_users_count_exception(fake_db_session):
    class FakeScalars:
        @staticmethod
        async def all():
            return []

        def __await__(self):
            return self.all().__await__()

    fake_db_session.scalars.return_value = FakeScalars()
    fake_db_session.scalar.side_effect = Exception("Count error")

    page = 1
    size = 10
    sort = Sort.ID
    order = Order.ASC

    with pytest.raises(Exception, match="Count error"):
        await list_users(page, size, sort, order, db=fake_db_session)
