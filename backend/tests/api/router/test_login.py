

from fastapi.testclient import TestClient
from fastapi import status

from app.core.config import settings
from app.models.user_model import UserCreate
from tests.utils.generate_random_data import (
    random_username,
    random_password,
) 


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER_NAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER_NAME,
        "password": "incorrect",
    }
    r = client.post(f"/login/access-token", data=login_data)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "name" in result


# def test_recovery_password(
#     client: TestClient, normal_user_token_headers: dict[str, str]
# ) -> None:
#     with (
#         patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
#         patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
#     ):
#         email = "test@example.com"
#         r = client.post(
#             f"/password-recovery/{email}",
#             headers=normal_user_token_headers,
#         )
#         assert r.status_code == 200
#         assert r.json() == {"message": "Password recovery email sent"}


# def test_recovery_password_user_not_exits(
#     client: TestClient, normal_user_token_headers: dict[str, str]
# ) -> None:
#     email = "jVgQr@example.com"
#     r = client.post(
#         f"/password-recovery/{email}",
#         headers=normal_user_token_headers,
#     )
#     assert r.status_code == 404


# def test_reset_password(client: TestClient, db: Session) -> None:
#     username = random_username()
#     password = random_password()
#     new_password = random_password()

#     user_create = UserCreate(
#         name=username,
#         password=password,
#         is_superuser=False,
#     )
#     user = create_user(session=db, user_create=user_create)
#     token = generate_password_reset_token(email=email)
#     headers = user_authentication_headers(client=client, email=email, password=password)
#     data = {"new_password": new_password, "token": token}

#     r = client.post(
#         f"/reset-password/",
#         headers=headers,
#         json=data,
#     )

#     assert r.status_code == 200
#     assert r.json() == {"message": "Password updated successfully"}

#     db.refresh(user)
#     assert verify_password(new_password, user.hashed_password)


# def test_reset_password_invalid_token(
#     client: TestClient, superuser_token_headers: dict[str, str]
# ) -> None:
#     data = {"new_password": "changethis", "token": "invalid"}
#     r = client.post(
#         f"/reset-password/",
#         headers=superuser_token_headers,
#         json=data,
#     )
#     response = r.json()

#     assert "detail" in response
#     assert r.status_code == 400
#     assert response["detail"] == "Invalid token"
