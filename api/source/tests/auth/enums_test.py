from source.app.auth.enums import TokenType


def test_token_type_values():
    # Проверяем, что значения Enum TokenType корректны
    assert TokenType.ACCESS.value == "access"
    assert TokenType.REFRESH.value == "refresh"


def test_token_type_membership():
    # Можно также проверить, что строковое значение можно использовать для получения члена Enum
    assert TokenType("access") == TokenType.ACCESS
    assert TokenType("refresh") == TokenType.REFRESH
