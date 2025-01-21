from typing import Any
import re
from pydantic import BaseModel


class UsernameStr(str):
    # ft 1-5

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str, field) -> str:
        check_latin = re.fullmatch(r"[A-Za-z]+", value) is not None
        check_length = 5 <= len(value) <= 64

        if not all([check_latin, check_length]):
            raise ValueError("Username must consist of Latin letters only and be between 5 and 64 characters long.")
        return value


class PasswordStr(str):
    # ft 1-4

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str, field) -> str:
        check_len = 256 >= len(value) >= 8
        check_latin = re.search(r"[A-Za-z]", value) is not None
        check_upper_lower = re.search(r"[A-Z]", value) and re.search(r"[a-z]", value)
        check_numbers = re.search(r"\d", value) is not None
        check_special = re.search(r'[!@#$%^&*(),.?":{}|<>=_]', value) is not None

        if not all([check_len, check_latin, check_upper_lower, check_numbers, check_special]):
            raise ValueError(
                "Password must be at least 8 characters long, include Latin letters (uppercase and lowercase), numbers, and a special character."
            )
        return value


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Credentials(BaseModel):
    username: UsernameStr
    password: PasswordStr


class Refresh(BaseModel):
    refresh_token: str
