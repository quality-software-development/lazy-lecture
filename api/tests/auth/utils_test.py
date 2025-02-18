from source.app.auth.utils import verify_password, get_password_hash


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции get_password_hash.
#   - Классы эквивалентности: исходный пароль (валидный формат)
#   и хешированный результат (непустая строка, отличная от исходного).
def test_get_password_hash_returns_non_empty_string():
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции verify_password для корректного ввода.
#   - Классы эквивалентности: совпадающие пароль и его хеш.
def test_verify_password_success():
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True


# Техника тест-дизайна: #4 Прогнозирование ошибок
# Автор: Юлиана Мирончук
# Описание:
#   - Тест функции verify_password для случая, когда введён неверный пароль.
#   - Таблица: сравнение корректного пароля и неверного – функция должна вернуть False.
def test_verify_password_failure():
    password = "StrongPass1!"
    wrong_password = "WrongPass1!"
    hashed = get_password_hash(password)
    assert verify_password(wrong_password, hashed) is False


# Техника тест-дизайна: #2 Граничные значения и #3 Причинно-следственный анализ
# Автор: Юлиана Мирончук
# Описание:
#   - Тест повторного хеширования одного и того же пароля.
#   - Границы: один и тот же исходный пароль должен давать разные хеши, так как применяется случайная соль.
def test_hash_is_different_for_same_password_due_to_salt():
    password = "StrongPass1!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2
