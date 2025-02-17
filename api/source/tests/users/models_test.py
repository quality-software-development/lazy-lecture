from source.app.users.models import User


def test_user_model_attributes():
    user = User()
    # Задаём поля вручную
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


def test_user_model_tablename():
    user = User()
    # __tablename__ должно быть "User"
    assert user.__tablename__ == "User"
