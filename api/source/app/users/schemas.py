from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

from source.app.auth.utils import get_password_hash
from source.app.users.enums import Order, Roles, Sort
from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema
from source.app.auth.schemas import Credentials, UsernameStr, PasswordStr


# class UserRequest(BaseModel):
#     username: str
#     password: str
UserRequest = Credentials


class UserCreate(UserRequest):
    active: bool = True
    role: Roles = Roles.USER
    password_timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())

    @model_validator(mode="after")
    def validator(cls, values: "UserCreate") -> "UserCreate":
        values.password = get_password_hash(values.password)
        return values


class UserResponse(ResponseSchema):
    username: UsernameStr
    active: bool
    can_interact: bool
    role: Roles
    create_date: datetime
    update_date: datetime


class UserUpdateRequest(BaseModel):
    # username: str | None = None is not alterable
    password: PasswordStr | None = None
    can_interact: bool | None = None


class UserUpdateRequestAdmin(UserUpdateRequest):
    active: bool | None = None
    role: Roles | None = None


class UserUpdate(UserUpdateRequestAdmin):
    password_timestamp: float | None = None

    @model_validator(mode="after")
    def validator(cls, values: "UserUpdate") -> "UserUpdate":
        if password := values.password:
            values.password = get_password_hash(password)
            values.password_timestamp = datetime.now(timezone.utc).timestamp()
        return values


class UserPage(PageSchema):
    users: list[UserResponse]


class UserPagination(PaginationSchema):
    sort: Sort = Sort.ID
    order: Order = Order.ASC


class UserId(BaseModel):
    user_id: int


class Username(BaseModel):
    username: UsernameStr
