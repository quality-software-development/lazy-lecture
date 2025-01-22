import re
import typing as tp
from typing_extensions import Annotated
from pydantic import (
    AfterValidator,
    PlainSerializer,
    TypeAdapter,
    WithJsonSchema,
)


def validate_username(value: str) -> str:
    # ft 1-5
    check_latin = re.fullmatch(r"[A-Za-z]+", value) is not None
    check_length = 5 <= len(value) <= 64

    if not all([check_latin, check_length]):
        raise ValueError("Username must consist of Latin letters only and be between 5 and 64 characters long.")
    return value


def validate_pass(value: str) -> str:
    # ft 1-4
    check_len = 256 >= len(value) >= 8
    check_latin = re.search(r"[A-Za-z]", value) is not None
    check_upper_lower = re.search(r"[A-Z]", value) and re.search(r"[a-z]", value)
    check_numbers = re.search(r"\d", value) is not None
    check_special = re.search(r'[!@#$%^&*(),.?":{}|<>=_]', value) is not None

    if not all([check_len, check_latin, check_upper_lower, check_numbers, check_special]):
        raise ValueError(
            "Password must be 8-256 characters long, include Latin letters (uppercase and lowercase), "
            "numbers, and at least one special character."
        )
    return value


PasswordStr = Annotated[
    str,
    AfterValidator(validate_pass),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
UsernameStr = Annotated[
    str,
    AfterValidator(validate_username),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
