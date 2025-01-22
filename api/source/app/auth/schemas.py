from pydantic import BaseModel

from source.app.auth.types import UsernameStr, PasswordStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Credentials(BaseModel):
    username: UsernameStr
    password: PasswordStr


class Refresh(BaseModel):
    refresh_token: str
