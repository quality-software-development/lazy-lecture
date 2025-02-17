from source.app.auth.utils import verify_password, get_password_hash


def test_get_password_hash_returns_non_empty_string():
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    # Хеш должен быть непустой строкой
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    # Хеш не должен совпадать с исходным паролем
    assert hashed != password


def test_verify_password_success():
    password = "StrongPass1!"
    hashed = get_password_hash(password)
    # Проверяем, что verify_password возвращает True для корректного пароля
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = "StrongPass1!"
    wrong_password = "WrongPass1!"
    hashed = get_password_hash(password)
    # Для неверного пароля verify_password должен вернуть False
    assert verify_password(wrong_password, hashed) is False


# Дополнительно можно протестировать, что хеш меняется при разных вызовах
def test_hash_is_different_for_same_password_due_to_salt():
    password = "StrongPass1!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    # Даже если пароли одинаковы, хеши, как правило, различны из-за случайной соли
    assert hash1 != hash2
