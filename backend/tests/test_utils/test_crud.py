from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.models.user_model import (
    User,
    UserCreate,
    UserUpdate,
)
from app.utils import crud
from tests.utils.generate_random_data import (
    random_password,
    random_username,
)


def test_check_if_user_is_superuser(session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password, is_superuser=True)
    user = crud.create_user(session=session, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password, is_superuser=True)
    user = crud.create_user(session=session, user_create=user_in)
    user_2 = session.get(User, user.id)
    assert user_2
    assert user.name == user_2.name
    assert user == user_2
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password, is_superuser=False)
    user = crud.create_user(session=session, user_create=user_in)
    new_password = random_password()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    crud.update_user(session=session, db_user=user, user_in=user_in_update)
    user_2 = session.get(User, user.id)
    assert user_2
    assert user.name == user_2.name
    assert verify_password(new_password, user_2.hashed_password)
