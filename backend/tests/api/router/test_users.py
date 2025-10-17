import uuid
from unittest.mock import patch  # noqa

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
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


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get("/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_superuser"]
    assert current_user["name"] == settings.FIRST_SUPERUSER_NAME


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get("/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["name"] == settings.TEST_NORMAL_USER_NAME


def test_create_user(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    # with (
    #     patch("app.utils.name", return_value=None),
    #     patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
    #     patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    # ):
    username = random_username()
    password = random_password()
    data = {"name": username, "password": password}
    r = client.post(
        "/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud.get_user_from_username(session=session, username=username)
    assert user
    assert user.name == created_user["name"]


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)
    user_id = user.id
    r = client.get(
        f"/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.get_user_from_username(session=session, username=username)
    assert existing_user
    assert existing_user.name == api_user["name"]


def test_get_existing_user_current_user(client: TestClient, session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)
    user_id = user.id

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post("/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = client.get(
        f"/users/{user_id}",
        headers=headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.get_user_from_username(session=session, username=username)
    assert existing_user
    assert existing_user.name == api_user["name"]


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"/users/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    crud.create_user(session=session, user_create=user_in)
    data = {"name": username, "password": password}
    r = client.post(
        "/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == status.HTTP_409_CONFLICT
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_username()
    password = random_password()
    data = {"name": username, "password": password}
    r = client.post(
        "/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    crud.create_user(session=session, user_create=user_in)

    username2 = random_username()
    password2 = random_password()
    user_in2 = UserCreate(name=username2, password=password2)
    crud.create_user(session=session, user_create=user_in2)

    r = client.get("/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "name" in item


def test_update_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str], session: Session
) -> None:
    secret_name = "Updated Secret Name"
    username = random_username()
    data = {"secret_name": secret_name, "name": username}
    r = client.patch(
        "/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["name"] == username
    assert updated_user["secret_name"] == secret_name

    user_session = crud.get_user_from_username(session, username)
    assert user_session
    assert user_session.name == username
    assert user_session.secret_name == secret_name

    # Revert to the old username to keep consistency in test
    user_update = UserUpdate(name=settings.TEST_NORMAL_USER_NAME)
    test_normal_user = crud.update_user(session, user_session, user_update)
    assert test_normal_user.name == settings.TEST_NORMAL_USER_NAME


def test_update_password_me(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    new_password = random_password()
    data = {
        "old_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = client.patch(
        "/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    user_session = crud.get_user_from_username(session, settings.FIRST_SUPERUSER_NAME)
    assert user_session
    assert user_session.name == settings.FIRST_SUPERUSER_NAME
    assert verify_password(new_password, user_session.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "old_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        "/users/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    session.refresh(user_session)

    assert r.status_code == 200
    assert verify_password(
        settings.FIRST_SUPERUSER_PASSWORD, user_session.hashed_password
    )


def test_update_password_me_incorrect_password(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    wrong_password = random_password()
    new_password = random_password()
    data = {"old_password": wrong_password, "new_password": new_password}
    r = client.patch(
        "/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


def test_update_name_exists(
    client: TestClient, normal_user_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)

    data = {"name": user.name}
    r = client.patch(
        "/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this name already exists"


def test_update_password_me_same_password_error(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "old_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        "/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 403
    updated_user = r.json()
    assert (
        updated_user["detail"] == "New password cannot be the same as the current one"
    )


def test_register_user(client: TestClient, session: Session) -> None:
    username = random_username()
    password = random_password()
    data = {"name": username, "password": password}
    r = client.post(
        "/users/signup",
        json=data,
    )
    assert r.status_code == status.HTTP_201_CREATED
    created_user = r.json()
    assert created_user["name"] == username

    user_session = crud.get_user_from_username(session, username)
    assert user_session
    assert user_session.name == username
    assert verify_password(password, user_session.hashed_password)


def test_register_user_already_exists_error(client: TestClient) -> None:
    password = random_username()
    secret_name = random_password()
    data = {
        "name": settings.FIRST_SUPERUSER_NAME,
        "password": password,
        "secret_name": secret_name,
    }
    r = client.post(
        "/users/signup",
        json=data,
    )
    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == "User with this name already exists"


def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)

    data = {"secret_name": "Updated_secret_name"}
    r = client.patch(
        f"/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()

    assert updated_user["secret_name"] == "Updated_secret_name"

    user_session = crud.get_user_from_username(session, username)
    session.refresh(user_session)
    assert user_session
    assert user_session.secret_name == "Updated_secret_name"


def test_update_user_not_exists(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"secret_name": "Updated_secret_name"}
    r = client.patch(
        f"/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


def name_exists(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)

    username2 = random_username()
    password2 = random_password()
    user_in2 = UserCreate(name=username2, password=password2)
    user2 = crud.create_user(session=session, user_create=user_in2)

    data = {"name": user2.name}
    r = client.patch(
        f"/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this name already exists"


def test_delete_user_me(client: TestClient, session: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)
    user_id = user.id

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post("/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = client.delete(
        "/users/me",
        headers=headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT
    result = session.exec(select(User).where(User.id == user_id)).first()
    assert result is None

    user_query = select(User).where(User.id == user_id)
    user_session = session.exec(user_query).first()
    assert user_session is None


def test_delete_user_me_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        "/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)
    user_id = user.id
    r = client.delete(
        f"/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT
    result = session.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    super_user = crud.get_user_from_username(
        session=session, username=settings.FIRST_SUPERUSER_NAME
    )
    assert super_user
    user_id = super_user.id

    r = client.delete(
        f"/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient, normal_user_token_headers: dict[str, str], session: Session
) -> None:
    username = random_username()
    password = random_password()
    user_in = UserCreate(name=username, password=password)
    user = crud.create_user(session=session, user_create=user_in)

    r = client.delete(
        f"/users/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"
