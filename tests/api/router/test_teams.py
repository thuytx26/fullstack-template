from sqlmodel import Session
from fastapi.testclient import TestClient


from .fixture import session_fixture, client_fixture
from app.models.team_model import Team


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