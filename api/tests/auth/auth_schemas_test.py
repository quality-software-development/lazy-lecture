import pytest
from pydantic import ValidationError
from source.app.auth.schemas import Token, Credentials, Refresh


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Token.
#   - Классы эквивалентности: корректные данные для access_token, refresh_token, а также проверка значения по умолчанию token_type.
def test_token_defaults():
    # Если token_type не передан, модель должна использовать значение по умолчанию ("bearer").
    token_data = {"access_token": "access123", "refresh_token": "refresh123"}
    token = Token(**token_data)
    assert token.access_token == "access123"
    assert token.refresh_token == "refresh123"
    assert token.token_type == "bearer"  # Значение по умолчанию


# Техника тест-дизайна: #5 Попарное тестирование
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Token с попарным перебором значений token_type.
#   - Таблица: комбинации "custom" и стандартного значения; проверяем, что при наличии явного token_type модель использует его.
def test_token_custom_token_type():
    # При наличии явного указания token_type модель должна использовать переданное значение.
    token_data = {"access_token": "access123", "refresh_token": "refresh123", "token_type": "custom"}
    token = Token(**token_data)
    assert token.token_type == "custom"


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Credentials.
#   - Классы эквивалентности: корректные значения для username (UsernameStr) и password (PasswordStr).
def test_credentials_valid():
    creds_data = {
        "username": "ValidUser",  # Корректное значение для UsernameStr
        "password": "StrongPass1!",  # Корректное значение для PasswordStr
    }
    creds = Credentials(**creds_data)
    assert creds.username == "ValidUser"
    assert creds.password == "StrongPass1!"


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Credentials.
#   - Таблица: сценарии отсутствия обязательных полей (username или password).
def test_credentials_invalid():
    with pytest.raises(ValidationError):
        Credentials(username="ValidUser")  # Ошибка: отсутствует поле password
    with pytest.raises(ValidationError):
        Credentials(password="StrongPass1!")  # Ошибка: отсутствует поле username


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Refresh.
#   - Классы эквивалентности: корректное значение для refresh_token.
def test_refresh_valid():
    data = {"refresh_token": "refresh_token_value"}
    refresh = Refresh(**data)
    assert refresh.refresh_token == "refresh_token_value"


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирочнук
# Описание:
#   - Тест для модели Refresh.
#   - Таблица: сценарий отсутствия обязательного поля refresh_token.
def test_refresh_invalid():
    with pytest.raises(ValidationError):
        Refresh()  # Ошибка: refresh_token отсутствует
