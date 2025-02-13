from typing import Annotated

from fastapi import Depends

from source.app.auth.services import auth, auth_admin, auth_can_interact
from source.app.users.models import User

CurrentUser = Annotated[User, Depends(auth)]
CanInteractCurrentUser = Annotated[User, Depends(auth_can_interact)]
Admin = Annotated[User, Depends(auth_admin)]

# # TODO: worker class
# Worker = Annotated[]
