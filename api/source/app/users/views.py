from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.auth.auth import CurrentUser
from source.app.users.models import User
from source.app.users.schemas import (
    UserRequest,
    UserResponse,
    UserUpdateRequest,
)
from source.app.users.services import create_user, get_user_by_id, update_user
from source.core.database import get_db
from source.core.exceptions import conflict
from source.core.schemas import ExceptionSchema
from source.app.transcriptions.types import validate_admin_token

users_router = APIRouter(prefix="/auth", tags=["auth"])


@users_router.post(
    "/register",
    response_model=UserResponse,
    responses={status.HTTP_409_CONFLICT: {"model": ExceptionSchema}},
    status_code=status.HTTP_201_CREATED,
)
async def user_create(user: UserRequest, db: AsyncSession = Depends(get_db)) -> User:
    if created_user := await create_user(user=user, db=db):
        return created_user
    return conflict(f"User '{user.username}' already exists")


@users_router.get(
    "/info",
    response_model=UserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def user_get(user: CurrentUser) -> User:
    return user


@users_router.patch(
    "/patch",
    response_model=UserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
    },
)
async def user_update(
    user_id: int,
    request: UserUpdateRequest,
    admin_secret_token: str = Depends(validate_admin_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    print(admin_secret_token)
    user = await get_user_by_id(user_id, db)
    if updated_user := await update_user(user=user, request=request, db=db):
        return updated_user
    return conflict(f"User '{request.username}' already exists")
