from datetime import datetime, timezone

import pytest

from source.app.users.enums import Roles
from source.app.users.models import User
from source.app.users.schemas import UserPage


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Классы:
# - Модель пользователя с корректно заданными полями
# (username, password, active, role, password_timestamp, can_interact)
def test_user_model_attributes():
    user = User()
    # Задаём поля вручную (типовой сценарий)
    user.username = "testuser"
    user.password = "hashed_password"
    user.active = True
    user.role = "user"
    user.password_timestamp = 1234567890.0
    user.can_interact = True

    assert user.username == "testuser"
    assert user.password == "hashed_password"
    assert user.active is True
    assert user.role == "user"
    assert user.password_timestamp == 1234567890.0
    assert user.can_interact is True


# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирончук
# Описание:
#   - Проверка создания UserPage с различными комбинациями параметров пагинации.
#   - Таблица: набор условий для расчёта количества страниц, общего числа и формирования списка пользователей.
#
# Комбинации:
#   1. Нет пользователей: total = 0, pages = 0.
#   2. Один пользователь на первой странице: total = 1, pages = 1.
#   3. Несколько пользователей, первая страница: total = 5, size = 2, pages = ceil(5/2) = 3.
#   4. Несколько пользователей, не первая страница: total = 5, size = 2, page = 2, pages = 3.
#
@pytest.mark.parametrize(
    "users_data, page, size, total, pages",
    [
        # Сценарий 1: Нет пользователей
        ([], 1, 10, 0, 0),
        # Сценарий 2: Один пользователь, первая страница
        ([{
            "id": 10,
            "username": "UserTest",
            "active": True,
            "can_interact": True,
            "role": Roles.USER,
            "create_date": datetime(2025, 1, 1, tzinfo=timezone.utc),
            "update_date": datetime(2025, 1, 1, tzinfo=timezone.utc)
        }], 1, 10, 1, 1),
        # Сценарий 3: Несколько пользователей, первая страница
        ([{
            "id": 11,
            "username": "UserA",
            "active": True,
            "can_interact": True,
            "role": Roles.USER,
            "create_date": datetime(2025, 1, 2, tzinfo=timezone.utc),
            "update_date": datetime(2025, 1, 2, tzinfo=timezone.utc)
        },
             {
                 "id": 12,
                 "username": "UserB",
                 "active": True,
                 "can_interact": False,
                 "role": Roles.USER,
                 "create_date": datetime(2025, 1, 2, tzinfo=timezone.utc),
                 "update_date": datetime(2025, 1, 2, tzinfo=timezone.utc)
             }], 1, 2, 5, 3),  # pages = ceil(5/2) = 3
        # Сценарий 4: Несколько пользователей, не первая страница
        ([{
            "id": 13,
            "username": "UserC",
            "active": True,
            "can_interact": True,
            "role": Roles.USER,
            "create_date": datetime(2025, 1, 3, tzinfo=timezone.utc),
            "update_date": datetime(2025, 1, 3, tzinfo=timezone.utc)
        }], 2, 2, 5, 3),  # На второй странице может оказаться меньше пользователей,
        # но общее число (total) и число страниц (pages) остаются теми же
    ]
)
def test_user_page_decision_table(users_data, page, size, total, pages):
    page_obj = UserPage(
        users=users_data,
        page=page,
        size=size,
        total=total,
        pages=pages
    )
    # Проверяем, что модель UserPage корректно сохраняет переданные параметры
    assert page_obj.page == page
    assert page_obj.size == size
    assert page_obj.total == total
    assert page_obj.pages == pages

    # Дополнительно, если список пользователей не пустой, проверяем корректность данных первого пользователя
    if users_data:
        first_user_input = users_data[0]
        first_user = page_obj.users[0]
        assert first_user.id == first_user_input["id"]
        assert first_user.username == first_user_input["username"]
