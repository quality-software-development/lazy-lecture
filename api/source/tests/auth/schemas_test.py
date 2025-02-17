import pytest
from pydantic import ValidationError

from source.app.auth.schemas import Token, Credentials, Refresh


# Для тестирования аннотированных типов мы можем использовать корректные строковые значения,
# так как UsernameStr и PasswordStr определяются в types.py.

# --- Тесты для модели Token ---

def test_token_defaults():
    # Если не передавать token_type, то по умолчанию должен быть "bearer"
    token_data = {
        "access_token": "access123",
        "refresh_token": "refresh123"
    }
    token = Token(**token_data)
    assert token.access_token == "access123"
    assert token.refresh_token == "refresh123"
    assert token.token_type == "bearer"  # значение по умолчанию


def test_token_custom_token_type():
    # Если явно указать token_type, то модель должна использовать его
    token_data = {
        "access_token": "access123",
        "refresh_token": "refresh123",
        "token_type": "custom"
    }
    token = Token(**token_data)
    assert token.token_type == "custom"


# --- Тесты для модели Credentials ---

def test_credentials_valid():
    # Корректные учетные данные должны создаваться без ошибок
    creds_data = {
        "username": "ValidUser",  # предполагается, что валидация UsernameStr допускает данное значение
        "password": "StrongPass1!"  # аналогично для PasswordStr
    }
    creds = Credentials(**creds_data)
    assert creds.username == "ValidUser"
    assert creds.password == "StrongPass1!"


def test_credentials_invalid():
    # Если не передать необходимые поля, должна возникать ошибка валидации
    with pytest.raises(ValidationError):
        Credentials(username="ValidUser")  # отсутствует password
    with pytest.raises(ValidationError):
        Credentials(password="StrongPass1!")  # отсутствует username


# --- Тесты для модели Refresh ---

def test_refresh_valid():
    # Корректное значение refresh_token должно создаваться без ошибок
    data = {"refresh_token": "refresh_token_value"}
    refresh = Refresh(**data)
    assert refresh.refresh_token == "refresh_token_value"


def test_refresh_invalid():
    # Если refresh_token отсутствует, должна быть ошибка валидации
    with pytest.raises(ValidationError):
        Refresh()
