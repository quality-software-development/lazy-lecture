from datetime import datetime, timedelta, timezone

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.auth.enums import TokenType
from source.app.auth.utils import verify_password
from source.app.users.enums import Roles
from source.app.users.models import User
from source.core.database import get_db
from source.core.exceptions import forbidden, unauthorized
from source.core.settings import settings


async def validate_user(user: User) -> User:
    if not user.active:
        return unauthorized("Your account is blocked")
    return user


async def authenticate_user(username: str, password: str, db: AsyncSession) -> User | None:
    user = await db.scalar(select(User).filter_by(username=username))
    if user and verify_password(plain_password=password, hashed_password=user.password):
        return await validate_user(user=user)
    return None


async def authenticate_token(
    user_id: int,
    password_timestamp: float,
    db: AsyncSession,
) -> User | None:
    user: User | None = await db.get(User, user_id)
    if user and password_timestamp == user.password_timestamp:
        return await validate_user(user=user)
    return None


async def generate_token(
    user_id: int,
    password_timestamp: float,
) -> dict:
    access = {
        "user_id": user_id,
        "password_timestamp": password_timestamp,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "token_type": TokenType.ACCESS,
    }
    refresh = access.copy()
    refresh.update(
        {
            "exp": datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "token_type": TokenType.REFRESH,
        }
    )
    access_token = jwt.encode(access, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    refresh_token = jwt.encode(refresh, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


async def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except (JWTError, ExpiredSignatureError, JWTClaimsError):
        return {}


async def authenticate_access_token(
    token: str, db: AsyncSession, roles: list | None = None, can_interact: bool | None = None
) -> User | None:
    payload = await decode_token(token)
    if payload and payload.get("token_type") == TokenType.ACCESS:
        if user := await authenticate_token(
            user_id=payload["user_id"],
            password_timestamp=payload["password_timestamp"],
            db=db,
        ):
            correct_role = not roles or user.role in roles
            correct_can_interact = not can_interact or user.can_interact == can_interact
            is_good = correct_role and correct_can_interact
            if is_good:
                return user
            else:
                return forbidden(f"Access restricted. Either your role or can_interact is invalid for the action.")
    return None


async def authenticate_refresh_token(token: str, db: AsyncSession) -> dict | None:
    payload = await decode_token(token)
    if payload and payload.get("token_type") == TokenType.REFRESH:
        if user := await authenticate_token(
            user_id=payload["user_id"],
            password_timestamp=payload["password_timestamp"],
            db=db,
        ):
            return await generate_token(
                user_id=user.id,
                password_timestamp=user.password_timestamp,
            )
    return None


async def authenticate(
    token: str, db: AsyncSession, roles: list | None = None, can_interact: bool | None = None
) -> User:
    if user := await authenticate_access_token(token=token, roles=roles, db=db, can_interact=can_interact):
        return user
    return unauthorized("Invalid or expired token")


async def auth(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        return unauthorized("Invalid Authorization Header")
    return await authenticate(token=token.credentials, db=db)


async def auth_admin(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        return unauthorized("Invalid Authorization Header")
    return await authenticate(token=token.credentials, db=db, roles=[Roles.ADMIN.value])


async def auth_can_interact(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        return unauthorized("Invalid Authorization Header")
    return await authenticate(token=token.credentials, db=db, can_interact=True)
