from sqlalchemy import Boolean, Column, Float, String

from source.core.models import Model


class User(Model):
    __tablename__ = "User"

    username = Column(name="username", type_=String, unique=True, index=True)
    password = Column(name="password", type_=String)
    active = Column(name="active", type_=Boolean)
    role = Column(name="role", type_=String)
    password_timestamp = Column(name="password_timestamp", type_=Float)
    can_interact = Column(name="can_interact", type_=Boolean, default=False)
