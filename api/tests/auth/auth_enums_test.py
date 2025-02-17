from source.app.auth.enums import TokenType


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Описание:
#   - Проверка корректности значений Enum для класса TokenType.
#   - Классы эквивалентности: корректные строковые значения, соответствующие членам TokenType.
def test_token_type_values():
    # Проверяем, что для TokenType.ACCESS и TokenType.REFRESH установлены ожидаемые значения.
    assert TokenType.ACCESS.value == "access"
    assert TokenType.REFRESH.value == "refresh"


# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Описание:
#   - Проверка преобразования строкового значения в элемент перечисления TokenType.
#   - Классы эквивалентности: корректные входные строки ("access", "refresh") соответствуют членам enum.
def test_token_type_membership():
    # Убедимся, что переданные строки корректно преобразуются в члены enum TokenType.
    assert TokenType("access") == TokenType.ACCESS
    assert TokenType("refresh") == TokenType.REFRESH
