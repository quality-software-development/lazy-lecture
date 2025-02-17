from source.app.auth.enums import TokenType

# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Корректные значения enum для TokenType
def test_token_type_values():
    # Проверяем, что значения Enum TokenType корректны для типичных (эквивалентных) входных данных.
    assert TokenType.ACCESS.value == "access"
    assert TokenType.REFRESH.value == "refresh"

# Техника тест-дизайна: #1 Классы эквивалентности
# Автор: Юлиана Мирочнук
# Классы:
# - Преобразование строки в enum для типичных значений
def test_token_type_membership():
    # Проверяем, что строковое значение корректно преобразуется в член enum.
    assert TokenType("access") == TokenType.ACCESS
    assert TokenType("refresh") == TokenType.REFRESH
