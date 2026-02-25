from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.team_model import (
    TeamCreate,
)
from app.utils import team_crud
from tests.utils.generate_random_data import (
    random_headquarters,
    random_skill_level,
    random_teamname,
)


def test_create_team(
    session: Session, client: TestClient, superuser_token_headers: dict[str, str]
):
    team_name = random_teamname()
    headquarters = random_headquarters()
    skill_level = random_skill_level()

    data = {"name": team_name, "headquarters": headquarters, "skill_level": skill_level}
    r = client.post("/teams", json=data, headers=superuser_token_headers)
    created_team = r.json()

    assert r.status_code == status.HTTP_201_CREATED
    assert "id" in created_team

    db_team = team_crud.get_team_from_name(session, team_name)
    assert db_team.headquarters == headquarters


def test_create_team_exists(
    session: Session,
    client: TestClient,
    superuser_token_headers: dict[str, str],
):
    team_name = random_teamname()
    team_to_create = TeamCreate(name=team_name)
    db_team = team_crud.create_team(session, team_to_create)
    assert "id" in db_team
    assert db_team.name == team_name

    team_name_2 = random_teamname()
    team_to_create_2 = TeamCreate(name=team_name_2)
    r = client.post("/teams", json=team_to_create_2, headers=superuser_token_headers)
    assert r.status_code == status.HTTP_409_CONFLICT


def test_create_team_normal_user(
    client: TestClient,
    normal_user_token_headers: dict[str, str],  # noqa: ARG001
):
    team_name = random_teamname()
    data = {"name": team_name}
    r = client.post(
        "/teams",
        json=data,
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN
