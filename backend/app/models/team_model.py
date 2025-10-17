import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ..models.user_model import User, UserPublic


class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True, max_length=255)
    headquarters: str | None = None
    skill_level: int | None = Field(default=1, ge=1, le=10)


class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    users: list["User"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: uuid.UUID


class TeamPublicWithUsers(TeamPublic):
    users: list["UserPublic"] = []


class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None
