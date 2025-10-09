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
from app.api.deps import SessionDep
from app.models.token_model import Token


router = APIRouter(tags=['login'])

@router.post('/login/access-token')
def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    incorrect_username_password_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    hero = crud.get_hero_from_username(session, form_data.username)

    if not hero:
        raise incorrect_username_password_exception

    if not verify_password(form_data.password, hero.hashed_password):
        raise incorrect_username_password_exception
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data = {"sub" : hero.name},
        expires_delta = expires_delta
    )

    return Token(access_token=access_token, token_type="bearer")
    







