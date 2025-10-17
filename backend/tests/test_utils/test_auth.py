from sqlmodel import Session

from app.core.security import settings
from app.utils import auth
from tests.utils.generate_random_data import random_password


def test_authenticate_user(session: Session):
    authenticated_user = auth.authentication(
        session=session,
        username=settings.FIRST_SUPERUSER_NAME,
        password=settings.FIRST_SUPERUSER_PASSWORD,
    )
    assert authenticated_user
    assert authenticated_user.name == settings.FIRST_SUPERUSER_NAME
    assert authenticated_user.is_superuser


def test_not_authenticate_user(session: Session):
    user = auth.authentication(
        session=session,
        username=settings.FIRST_SUPERUSER_NAME,
        password=random_password(),
    )
    assert user is None
