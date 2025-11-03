import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.deps import get_session
from app.core.config import settings
from app.core.database import engine, init_db
from app.main import app
from tests.utils.users import (
    get_normal_user_token_headers,
    get_superuser_token_headers,
)


@pytest.fixture(name="session", scope="module")
def session_fixture():
    # engine = create_engine(
    #     "sqlite://",
    #     connect_args={"check_same_thread": False},
    #     poolclass=StaticPool,
    # )
    # SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        init_db(session)
        yield session


@pytest.fixture(name="client", scope="module")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    client.base_url = str(client.base_url) + settings.API_V1_STR
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser_token_headers", scope="module")
def superuser_token_headers_fixture(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(name="normal_user_token_headers", scope="module")
def normal_user_token_headers_fixture(
    client: TestClient,
    session: Session,
) -> dict[str, str]:
    return get_normal_user_token_headers(
        client=client,
        session=session,
        username=settings.TEST_NORMAL_USER_NAME,
    )
