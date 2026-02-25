import uuid

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import (
    Session,
    select,
)

from app.models.team_model import (
    Team,
    TeamCreate,
    TeamUpdate,
)


def get_team_from_name(session: Session, name: str) -> Team | None:
    statement = select(Team).where(Team.name == name)
    team = session.exec(statement)
    return team


def create_team(
    session: Session,
    team: TeamCreate,
):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


def update_team(
    team_id: uuid.UUID,
    team: TeamUpdate,
    session: Session,
):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


def delete_team(
    team_id: uuid.UUID,
    session: Session,
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    session.delete(team)
    session.commit()
