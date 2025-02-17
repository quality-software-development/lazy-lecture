from source.app.auth.utils import verify_password, get_password_hash


def test_get_password_hash_returns_non_empty_string():
    # Техника тест-дизайна: #1 Классы эквивалентности
    # Автор: Юлиана Мирочнук
    # Классы:
    # - Исходный пароль корректного формата
    # - Хешированный пароль (должен быть строкой, непустой и отличаться от исходного)
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password


def test_verify_password_success():
    # Техника тест-дизайна: #1 Классы эквивалентности
    # Автор: Юлиана Мирочнук
    # Классы:
    # - Корректный пароль и его хеш
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    # Техника тест-дизайна: #4 Прогнозирование ошибок
    # Автор: Юлиана Мирочнук
    # Классы:
    # - Корректный пароль и неверный пароль
    password = "StrongPass1!"
    wrong_password = "WrongPass1!"
    hashed = get_password_hash(password)
    assert verify_password(wrong_password, hashed) is False


def test_hash_is_different_for_same_password_due_to_salt():
    # Техника тест-дизайна: #2 Граничные значения и #3 Причинно-следственный анализ
    # Автор: Юлиана Мирочнук
    # Классы:
    # - Один и тот же исходный пароль
    # - Два разных хеша, полученные из-за случайной соли
    password = "StrongPass1!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2
