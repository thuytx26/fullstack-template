from typing import Annotated
from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import OAuth2PasswordRequestForm


from app.utils import crud
from app.core.security import (
    verify_password,
    create_access_token
)
from app.core.config import settings
from app.api.deps import (
    SessionDep,
    CurrentUserDep
)
from app.models.token_model import Token
from app.models.user_model import UserPublic
from app.utils import auth


router = APIRouter(tags=['login'])

@router.post('/login/access-token', status_code=status.HTTP_200_OK)
def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):

    incorrect_username_password_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth.authentication(
        session=session,
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise incorrect_username_password_exception
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data = {"sub" : user.name},
        expires_delta = expires_delta
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    '/login/test-token', 
    response_model=UserPublic,
    status_code=status.HTTP_200_OK
)
def test_token(current_user: CurrentUserDep):
    return current_user