from source.app.users.models import User


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Модель пользователя с корректно заданными полями
def test_user_model_attributes():
    user = User()
    # Задаём поля вручную (типовой сценарий)
    user.username = "testuser"
    user.password = "hashed_password"
    user.active = True
    user.role = "user"
    user.password_timestamp = 1234567890.0
    user.can_interact = True

    # Проверяем, что поля установлены корректно
    assert user.username == "testuser"
    assert user.password == "hashed_password"
    assert user.active is True
    assert user.role == "user"
    assert user.password_timestamp == 1234567890.0
    assert user.can_interact is True


# Техника тест-дизайна: #7 Таблица принятия решений
# Автор: Юлиана Мирочнук
# Классы:
# - Проверка значения __tablename__
def test_user_model_tablename():
    user = User()
    # Ожидаем, что __tablename__ равно "User"
    assert user.__tablename__ == "User"
