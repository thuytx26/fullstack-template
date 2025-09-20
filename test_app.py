from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
import pytest
import uuid

from .app  import app
from .database import get_session
from .models.team_model import Team
from .models.hero_model import Hero


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_team(client: TestClient):

    response = client.post("/teams/", json={"name": "Avengers", "headquarters": "New York"})
    
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Avengers"
    assert data["headquarters"] == "New York"
        
def test_create_team_invalid(client: TestClient):
    # missing name field
    response = client.post("/teams/", json={"headquarters": "New York"})
    assert response.status_code == 422

def test_read_teams(session: Session, client: TestClient):
    team1_name = "Avengers"
    team2_name = "Justice League"
    team1_hq = "New York"
    team2_hq = "Metropolis"
    team1 = {"name": team1_name, "headquarters": team1_hq}
    team2 = {"name": team2_name, "headquarters": team2_hq}
    session.add(Team.model_validate(team1))
    session.add(Team.model_validate(team2))
    session.commit()
    
    response = client.get("/teams/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == team1_name
    assert data[1]["name"] == team2_name

def test_create_hero(client: TestClient):
    response = client.post(
        "/heroes/", json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Deadpond"
    assert data["secret_name"] == "Dive Wilson"
    assert data["age"] is None
    assert data["id"] is not None


def test_create_hero_invalid(client: TestClient):
    # No secret_name
    response = client.post("/heroes/", json={"name": "Deadpond"})
    assert response.status_code == 422


def test_read_heroes(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    session.add(hero_1)
    session.add(hero_2)
    session.commit()

    response = client.get("/heroes/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    response_names = {h["name"] for h in data}
    assert response_names == {hero_1.name, hero_2.name}


def test_read_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson", age=28)
    session.add(hero_1)
    session.commit()
    session.refresh(hero_1)

    response = client.get(f"/heroes/{hero_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == hero_1.name
    assert data["secret_name"] == hero_1.secret_name
    assert data["age"] == hero_1.age
    assert data["id"] == str(hero_1.id)


def test_update_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson", age=28)
    session.add(hero_1)
    session.commit()
    session.refresh(hero_1)
    response = client.patch(f"/heroes/{hero_1.id}", json={"name": "Deadpuddle"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Deadpuddle"
    assert data["secret_name"] == hero_1.secret_name
    assert data["id"] == str(hero_1.id)

    db_hero = session.get(Hero, hero_1.id)
    assert db_hero.name == "Deadpuddle"


def test_delete_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson", age=28)
    session.add(hero_1)
    session.commit()
    session.refresh(hero_1)

    response = client.delete(f"/heroes/{hero_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == hero_1.name

    deleted_hero = session.get(Hero, hero_1.id)
    assert deleted_hero is None


def test_create_hero_with_team(session: Session, client: TestClient):
    team = Team(name="Justice League", headquarters="Metropolis")
    session.add(team)
    session.commit()
    session.refresh(team)

    response = client.post(
        "/heroes/",
        json={
            "name": "Superman",
            "secret_name": "Clark Kent",
            "team_id": str(team.id),
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Superman"
    assert data["team_id"] == str(team.id)

    hero_in_db = session.get(Hero, uuid.UUID(data["id"]))
    assert hero_in_db.team.name == team.name


    