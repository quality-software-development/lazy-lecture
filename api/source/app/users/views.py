from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.auth.auth import Admin, CurrentUser
from source.app.users.models import User
from source.app.users.schemas import (
    UserPage,
    UserPagination,
    UserRequest,
    UserResponse,
    UserUpdateRequest,
)
from source.app.users.services import create_user, delete_user, list_users, update_user
from source.core.database import get_db
from source.core.exceptions import conflict
from source.core.schemas import ExceptionSchema

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
    user: CurrentUser,
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    if updated_user := await update_user(user=user, request=request, db=db):
        return updated_user
    return conflict(f"User '{request.username}' already exists")


# @users_router.delete(
#     "/",
#     responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["users"],
# )
# async def user_delete(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> None:
#     await delete_user(user=user, db=db)
#     return None


# @users_router.get(
#     "/admin",
#     response_model=UserPage,
#     responses={
#         status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
#         status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
#     },
#     tags=["admin"],
# )
# async def users_list(
#     user: Admin,
#     pagination: UserPagination = Depends(),
#     db: AsyncSession = Depends(get_db),
# ) -> UserPage:
#     return await list_users(
#         page=pagination.page,
#         size=pagination.size,
#         sort=pagination.sort,
#         order=pagination.order,
#         db=db,
#     )
