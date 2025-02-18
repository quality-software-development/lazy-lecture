import pytest
from pydantic import BaseModel, ValidationError
from source.app.auth.types import validate_username, validate_pass, UsernameStr, PasswordStr


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции validate_username.
#   - Классы эквивалентности: корректные строки для username,
#   представляющие минимальное, типичное и максимальное допустимое значение.


@pytest.mark.parametrize(
    "username",
    [
        "Alice",  # минимальная длина (нижняя граница)
        "JohnDoe",  # типичный случай (среднее значение)
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",  # максимально допустимое значение (верхняя граница)
    ],
)
def test_validate_username_valid(username):
    result = validate_username(username)
    assert result == username


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции validate_username.
#   - Таблица: набор невалидных значений для username
#   (слишком короткий, содержит цифры, кириллица, недопустимые символы, превышает максимальную длину).
@pytest.mark.parametrize(
    "username",
    [
        "Bob",  # меньше минимальной длины
        "123456",  # содержит цифры вместо латинских букв
        "Алиса",  # кириллица
        "John_Doe",  # содержит недопустимые символы
        "a" * 65,  # превышает максимальную длину
    ],
)
def test_validate_username_invalid(username):
    with pytest.raises(ValueError) as exc_info:
        validate_username(username)
    assert "Username must consist of Latin letters only and be between 5 and 64 characters long." in str(exc_info.value)


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции validate_pass.
#   - Классы эквивалентности: корректные пароли, соответствующие требованиям
#   (наличие заглавных, строчных, цифр и спецсимволов).
@pytest.mark.parametrize(
    "password",
    [
        "Abcd1234!",  # типичный корректный пароль
        "Password1@",  # типичный корректный пароль
        "A1b2C3d4$",  # типичный корректный пароль
    ],
)
def test_validate_pass_valid(password):
    result = validate_pass(password)
    assert result == password


# Техника тест-дизайна: #2 Граничные значения и #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции validate_pass.
#   - Таблица: набор невалидных паролей с граничными значениями и ошибками
#   (слишком короткий, отсутствие заглавных, строчных, цифр, спецсимволов, слишком длинный).
@pytest.mark.parametrize(
    "password",
    [
        "Ab1!",  # слишком короткий (нижняя граница)
        "abcd1234!",  # отсутствуют заглавные буквы
        "ABCD1234!",  # отсутствуют строчные буквы
        "Abcdefgh!",  # отсутствуют цифры
        "Abcd1234",  # отсутствует спецсимвол
        "A" * 257,  # слишком длинный (верхняя граница)
    ],
)
def test_validate_pass_invalid(password):
    with pytest.raises(ValueError) as exc_info:
        validate_pass(password)
    EXPECTED_PASS_ERROR = (
        "Password must be 8-256 characters long, include Latin letters (uppercase and lowercase), numbers, "
        "and at least one special character."
    )
    assert EXPECTED_PASS_ERROR.strip() == str(exc_info.value).strip()


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тест создания модели с аннотированными типами для username и password.
#   - Классы эквивалентности: корректное создание объекта класса UserModel с валидными значениями.
class UserModel(BaseModel):
    username: UsernameStr
    password: PasswordStr


def test_model_valid():
    data = {"username": "ValidName", "password": "StrongPass1!"}
    user = UserModel(**data)
    assert user.username == data["username"]
    assert user.password == data["password"]


# Техника тест-дизайна: #7 Таблица принятия решений и #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Тест для модели UserModel с невалидными данными.
#   - Таблица: различные комбинации ошибок для username и password, где для каждого поля описывается ожидаемая ошибка.
@pytest.mark.parametrize(
    "data, error_field, expected_error_fragment",
    [
        (
            {"username": "Bob", "password": "StrongPass1!"},
            "username",
            "Username must consist of Latin letters only and be between 5 and 64 characters long.",
        ),
        (
            {"username": "ValidName", "password": "weak"},
            "password",
            "Password must be 8-256 characters long",
        ),
    ],
)
def test_model_invalid(data, error_field, expected_error_fragment):
    with pytest.raises(ValidationError) as exc_info:
        UserModel(**data)
    errors = exc_info.value.errors()
    error_messages = [err["msg"] for err in errors if err["loc"][0] == error_field]
    assert any(expected_error_fragment in msg for msg in error_messages)
