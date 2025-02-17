import pytest
from pydantic import BaseModel, ValidationError

# Импортируем тестируемые функции и аннотированные типы
from source.app.auth.types import validate_username, validate_pass, UsernameStr, PasswordStr

# Общая константа ожидаемого сообщения об ошибке для пароля
EXPECTED_PASS_ERROR = (
    "Password must be 8-256 characters long, include Latin letters (uppercase and lowercase), numbers, "
    "and at least one special character."
)


# --- Тесты для validate_username ---

@pytest.mark.parametrize("username", [
    "Alice",  # Минимальная длина 5
    "JohnDoe",  # Обычный вариант
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"  # 52 символа, допустимо
])
def test_validate_username_valid(username):
    # Если username корректен, функция должна вернуть его без изменений
    result = validate_username(username)
    assert result == username


@pytest.mark.parametrize("username", [
    "Bob",  # меньше 5 символов
    "123456",  # содержит цифры (не латинские буквы)
    "Алиса",  # кириллица
    "John_Doe",  # символ подчеркивания недопустим
    "a" * 65  # больше 64 символов
])
def test_validate_username_invalid(username):
    with pytest.raises(ValueError) as exc_info:
        validate_username(username)
    # Проверяем, что текст ошибки содержит ожидаемое сообщение
    assert "Username must consist of Latin letters only and be between 5 and 64 characters long." in str(exc_info.value)


# --- Тесты для validate_pass ---

@pytest.mark.parametrize("password", [
    "Abcd1234!",  # Содержит: длину 9, латинские буквы, заглавную, строчную, цифры и спецсимвол
    "Password1@",  # Другой корректный пример
    "A1b2C3d4$"  # Корректный вариант
])
def test_validate_pass_valid(password):
    # Для корректного пароля функция должна вернуть пароль без изменений
    result = validate_pass(password)
    assert result == password


@pytest.mark.parametrize("password", [
    "Ab1!",  # Недостаточная длина и не проходит остальные проверки
    "abcd1234!",  # Нет заглавных букв
    "ABCD1234!",  # Нет строчных букв
    "Abcdefgh!",  # Нет цифр
    "Abcd1234",  # Нет спецсимвола
    "A" * 257  # Слишком длинный пароль (257 символов)
])
def test_validate_pass_invalid(password):
    with pytest.raises(ValueError) as exc_info:
        validate_pass(password)
    # Сравниваем полученное сообщение об ошибке с EXPECTED_PASS_ERROR
    assert EXPECTED_PASS_ERROR.strip() == str(exc_info.value).strip()


# --- Тесты для аннотированных типов через Pydantic-модель ---

class UserModel(BaseModel):
    username: UsernameStr
    password: PasswordStr


def test_model_valid():
    # Корректные данные для модели
    data = {
        "username": "ValidName",
        "password": "StrongPass1!"
    }
    user = UserModel(**data)
    assert user.username == data["username"]
    assert user.password == data["password"]


@pytest.mark.parametrize("data, error_field, expected_error_fragment", [
    ({"username": "Bob", "password": "StrongPass1!"}, "username",
     "Username must consist of Latin letters only and be between 5 and 64 characters long."),
    ({"username": "ValidName", "password": "weak"}, "password", "Password must be 8-256 characters long")
])
def test_model_invalid(data, error_field, expected_error_fragment):
    with pytest.raises(ValidationError) as exc_info:
        UserModel(**data)
    errors = exc_info.value.errors()
    # Проверяем, что в списке ошибок есть ошибка для нужного поля с ожидаемым фрагментом сообщения
    error_messages = [err['msg'] for err in errors if err['loc'][0] == error_field]
    assert any(expected_error_fragment in msg for msg in error_messages)
