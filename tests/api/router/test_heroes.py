from fastapi.testclient import TestClient
from sqlmodel import Session
import uuid


from .fixture import session_fixture, client_fixture
from app.models.hero_model import Hero
from app.models.team_model import Team


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


    