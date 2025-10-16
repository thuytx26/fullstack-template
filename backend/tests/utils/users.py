from sqlmodel import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.generate_random_data import (
    random_username,
    random_password,
)
from app.models.user_model import (
    User, 
    UserRegister,
    UserUpdate
)
from app.utils import crud


def user_authentication_headers(
    client: TestClient,
    username: str,
    password: str
) -> dict[str, str]:
    response = client.post(
        f"/login/access-token", 
        data={
            "username": username, 
            "password": password,
        }
    )
    response = response.json()
    access_token = response['access_token']
    header = {"Authorization": f"Bearer {access_token}"}
    return header


def get_superuser_token_headers(
    client: TestClient
) -> dict[str, str]:
    return user_authentication_headers(
        client=client,
        username=settings.FIRST_SUPERUSER_NAME,
        password=settings.FIRST_SUPERUSER_PASSWORD,
    )


def get_normal_user_token_headers(
    *,
    client: TestClient,
    session: Session,
    username: str,
) -> dict[str, str]:
    password = random_password()
    
    existing_user = crud.get_user_from_username(session, username)
    if not existing_user:
        user_in = UserRegister(
            name=username,
            password=password,
        )
        crud.create_user(
            session,
            user_create=user_in,
        )
    else:
        if existing_user.id is None:
            raise Exception("User id is None")
        user_update = UserUpdate(
            password=password,
        )
        crud.update_user(
            session,
            db_user=existing_user,
            user_in=user_update,
        )

    return user_authentication_headers(
        client=client,
        username=username,
        password=password,
    )
    

    