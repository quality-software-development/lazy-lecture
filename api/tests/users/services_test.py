from datetime import datetime, timezone
from math import ceil
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


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Проверка валидного запроса для создания пользователя.
#   - Классы: корректный экземпляр UserRequest с валидными значениями.
@pytest.fixture
def fake_user_request():
    return UserRequest(username="testuser", password="StrongPass1!")


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Проверка сценария создания пользователя с невалидными данными.
#   - Таблица: набор условий, при которых username не проходит валидацию.
@pytest.fixture
def fake_invalid_user_request():
    return {"username": "123", "password": "StrongPass1!"}


def fake_user():
    test_user = User()
    test_user.username = "testuser"
    test_user.password = "old_hash"
    test_user.active = True
    test_user.role = "user"
    test_user.can_interact = False
    return test_user


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
# - Замоканная сессия БД для типичных сценариев
@pytest.fixture
def fake_db_session():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.get_one = AsyncMock()
    db.scalar = AsyncMock()
    db.scalars = MagicMock()
    db.delete = AsyncMock()
    return db


# =================== Тесты для create_user ===================

@pytest.mark.asyncio
async def test_create_user_success(fake_user_request, fake_db_session, monkeypatch):
    # Техника тест-дизайна: #1 Классы эквивалентности
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Типовой сценарий успешного создания пользователя.
    #   - Классы: валидный UserRequest, корректное преобразование пароля.
    def fake_hash(pw: str) -> str:
        return f"hashed_{pw}"

    monkeypatch.setattr("source.app.users.schemas.get_password_hash", fake_hash)

    fake_db_session.commit.return_value = None
    fake_db_session.refresh.return_value = None

    created_user = await create_user(user=fake_user_request, db=fake_db_session)
    assert isinstance(created_user, User)
    assert created_user.password == f"hashed_{fake_user_request.password}"


@pytest.mark.asyncio
async def test_create_user_integrity_error(fake_user_request, fake_db_session):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий, когда возникает IntegrityError при коммите (например, дублирование записи).
    #   - Таблица: набор условий, при которых commit выбрасывает исключение.
    fake_db_session.commit.side_effect = IntegrityError("dummy", "params", Exception("dummy"))
    result = await create_user(user=fake_user_request, db=fake_db_session)
    assert result is None


@pytest.mark.asyncio
async def test_create_user_invalid_input(fake_invalid_user_request, fake_db_session):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий: создание пользователя с невалидными данными должно вызвать исключение.
    #   - Таблица: условие невалидного ввода (например, неверный username).
    with pytest.raises(Exception):
        await create_user(user=fake_invalid_user_request, db=fake_db_session)


# =================== Тесты для get_user_by_id ===================

@pytest.mark.asyncio
async def test_get_user_by_id_found(fake_db_session):
    # Техника тест-дизайна: #1 Классы эквивалентности
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Типовой сценарий, когда пользователь найден в БД.
    #   - Классы: корректный пользователь, возвращаемый методом get_one.
    test_user = User()
    test_user.username = "testuser"
    fake_db_session.get_one.return_value = test_user

    user = await get_user_by_id(user_id=1, db=fake_db_session)
    fake_db_session.get_one.assert_called_once_with(User, 1)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(fake_db_session):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий, когда пользователь не найден в БД (get_one возвращает None).
    #   - Таблица: набор условий для несуществующего пользователя.
    fake_db_session.get_one.return_value = None
    user = await get_user_by_id(user_id=999, db=fake_db_session)
    assert user is None


# =================== Тесты для update_user ===================


@pytest.mark.asyncio
async def test_update_user_success(fake_db_session, monkeypatch):
    # Техника тест-дизайна: #3 Причинно-следственный анализ
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Типовой сценарий обновления: изменение пароля и поля can_interact.
    #   - Классы: пользователь, для которого изменяются пароль и возможность взаимодействия.
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


@pytest.mark.asyncio
async def test_update_user_no_changes(fake_db_session):
    # Техника тест-дизайна: #2 Граничные значения и #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Граничный сценарий: пустой запрос обновления не должен изменять данные пользователя.
    #   - Границы: отсутствие изменений, пользователь остаётся неизменным.
    test_user = User()
    test_user.username = "testuser"
    test_user.password = "old_hash"
    test_user.active = True
    test_user.role = "user"
    test_user.can_interact = False

    update_data = {}  # Пустой запрос
    update_request = UserUpdateRequest(**update_data)

    fake_db_session.commit.return_value = None
    fake_db_session.refresh.return_value = None

    updated_user = await update_user(user=test_user, request=update_request, db=fake_db_session)
    assert updated_user.password == "old_hash"
    assert updated_user.can_interact is False


@pytest.mark.asyncio
async def test_update_user_integrity_error(fake_db_session, monkeypatch):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий: при обновлении возникает IntegrityError (например, конфликт обновления).
    #   - Таблица: набор условий, при которых commit выбрасывает исключение.
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
    # Техника тест-дизайна: #1 Классы эквивалентности
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Типовой сценарий успешного удаления пользователя.
    #   - Классы: корректный пользователь, который успешно удаляется.
    test_user = User()
    await delete_user(user=test_user, db=fake_db_session)
    fake_db_session.delete.assert_called_once_with(test_user)
    fake_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_exception(fake_db_session):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий: удаление пользователя вызывает исключение (например, ошибка при commit).
    #   - Таблица: набор условий, при которых метод удаления выбрасывает исключение.
    test_user = User()
    fake_db_session.delete.side_effect = Exception("Delete error")
    with pytest.raises(Exception, match="Delete error"):
        await delete_user(user=test_user, db=fake_db_session)


# =================== Тесты для list_users ===================


@pytest.mark.asyncio
async def test_list_users_success(fake_db_session):
    # Техника тест-дизайна: #1 Классы эквивалентности и #7 Таблица принятия решений
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Типовой сценарий: База содержит два пользователя.
    #   - Классы: корректные ORM-объекты пользователей.
    #   - Таблица: набор условий для вычисления числа страниц, общего числа пользователей и формирования ответа.
    now = datetime.now(timezone.utc)
    user1 = User(id=1, username="UserOne", active=True, can_interact=True, role=Roles.USER, password_timestamp=123456.0)
    user1.create_date = now
    user1.update_date = now

    user2 = User(id=2, username="UserTwo", active=True, can_interact=False, role=Roles.USER,
                 password_timestamp=123456.0)
    user2.create_date = now
    user2.update_date = now

    users_list = [user1, user2]

    class FakeScalars:
        @staticmethod
        async def all():
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
    # Техника тест-дизайна: #3 Причинно-следственный анализ
    # Сравниваем представления ORM-объектов и схемы UserResponse
    expected = [UserResponse.from_orm(u).dict() for u in users_list]
    actual = [r.dict() for r in user_page.users]
    assert actual == expected


@pytest.mark.asyncio
async def test_list_users_empty(fake_db_session):
    # Техника тест-дизайна: #2 Граничные значения
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Граничный сценарий: если пользователей нет, общее число (total) равно 0, список пустой.
    #   - Границы: проверка нулевого значения total и корректного расчёта числа страниц.
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
    assert user_page.pages == 0
    assert user_page.users == []


@pytest.mark.asyncio
async def test_list_users_count_exception(fake_db_session):
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирончук
    # Описание:
    #   - Сценарий: если db.scalar (подсчёт записей) выбрасывает исключение, тест должен его отловить.
    #   - Таблица: условие, при котором подсчёт записей не выполняется корректно.
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
