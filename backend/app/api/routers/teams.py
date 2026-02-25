import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from sqlmodel import select

from app.api.deps import (
    SessionDep,
    get_current_superuser,
)
from app.models.team_model import (
    Team,
    TeamCreate,
    TeamPublic,
    TeamPublicWithUsers,
    TeamUpdate,
)
from app.utils import team_crud

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
)


@router.post(
    "/",
    dependencies=[
        Depends(get_current_superuser),
    ],
    response_model=TeamPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    *,
    team: Annotated[TeamCreate, Body(title="Team to create")],
    session: SessionDep,
):
    db_team = team_crud.create_team(session, team)
    return db_team


@router.get(
    "/{team_id}",
    dependencies=[
        Depends(get_current_superuser),
    ],
    response_model=TeamPublicWithUsers,
)
def read_team(*, team_id: uuid.UUID, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@router.get(
    "/",
    dependencies=[
        Depends(get_current_superuser),
    ],
    response_model=list[TeamPublic],
)
def read_teams(*, session: SessionDep, offset: int = 0, limit: int = 100):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams


@router.patch(
    "/{team_id}",
    dependencies=[
        Depends(get_current_superuser),
    ],
    response_model=TeamPublic,
)
def update_team(*, team_id: uuid.UUID, team: TeamUpdate, session: SessionDep):
    db_team = team_crud.update_team(team_id, team, session)
    return db_team


@router.delete(
    "/{team_id}",
    dependencies=[
        Depends(get_current_superuser),
    ],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team(*, team_id: uuid.UUID, session: SessionDep):
    team_crud.delete_team(team_id, session)
