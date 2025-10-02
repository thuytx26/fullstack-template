from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException,
    Body,
    Path,
    Query,
)
import uuid
from sqlmodel import select, Session
from typing import Annotated

from ..database import get_session

from ..models.team_model import (
    Team,
    TeamCreate,
    TeamPublic,
    TeamUpdate,
    TeamPublicWithHeroes,
)

from ..models.hero_model import Hero


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
)

@router.post("/", response_model=TeamPublic)
def create_team(
    *,
    team: Annotated[TeamCreate, Body(title="Team to create")],
    session: Session = Depends(get_session)
    ):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team
    

@router.get("/{team_id}", response_model=TeamPublicWithHeroes)
def read_team(*, team_id: uuid.UUID, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/", response_model=list[TeamPublic])
def read_teams(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams


@router.patch("/{team_id}", response_model=TeamPublic)
def update_team(*, team_id: uuid.UUID, team: TeamUpdate, session: Session = Depends(get_session)):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.delete("/{team_id}", response_model=TeamPublic)
def delete_team(*, team_id: uuid.UUID, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return team