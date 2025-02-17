import pytest
from pydantic import ValidationError
from source.app.auth.schemas import Token, Credentials, Refresh


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Стандартное поведение модели Token (без явного указания token_type)
def test_token_defaults():
    # Если token_type не передан, должен использоваться дефолтный "bearer"
    token_data = {"access_token": "access123", "refresh_token": "refresh123"}
    token = Token(**token_data)
    assert token.access_token == "access123"
    assert token.refresh_token == "refresh123"
    assert token.token_type == "bearer"  # Значение по умолчанию


# Техника тест-дизайна: #5 Попарное тестирование
# Автор: Юлиана Мирочнук
# Классы:
# - Разные значения token_type (custom и стандартное)
def test_token_custom_token_type():
    # Если явно указан token_type, модель должна его использовать
    token_data = {"access_token": "access123", "refresh_token": "refresh123", "token_type": "custom"}
    token = Token(**token_data)
    assert token.token_type == "custom"


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректные учетные данные
def test_credentials_valid():
    creds_data = {
        "username": "ValidUser",  # Допустимое значение для UsernameStr
        "password": "StrongPass1!",  # Допустимое значение для PasswordStr
    }
    creds = Credentials(**creds_data)
    assert creds.username == "ValidUser"
    assert creds.password == "StrongPass1!"


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирочнук
# Классы:
# - Отсутствие обязательных полей (username или password)
def test_credentials_invalid():
    with pytest.raises(ValidationError):
        Credentials(username="ValidUser")  # password отсутствует
    with pytest.raises(ValidationError):
        Credentials(password="StrongPass1!")  # username отсутствует


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректное значение refresh_token
def test_refresh_valid():
    data = {"refresh_token": "refresh_token_value"}
    refresh = Refresh(**data)
    assert refresh.refresh_token == "refresh_token_value"


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирочнук
# Классы:
# - Отсутствие refresh_token
def test_refresh_invalid():
    with pytest.raises(ValidationError):
        Refresh()
