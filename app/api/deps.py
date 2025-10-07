from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlmodel import Session
from typing import Annotated


from app.core.database import engine
from app.models.hero_model import HeroBase


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


TokenDep = Annotated[str, Depends(oauth2_scheme)]


def fake_decode_token(token):
    return HeroBase(
        name=token + 'test',
        secret_name='test',
    )

async def get_current_user(token: TokenDep):
    user = fake_decode_token(token)
    return user

CurrentUser = Annotated[HeroBase, Depends(get_current_user)]