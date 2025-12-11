import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ..models.user_model import User, UserPublic


class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True, max_length=255)
    headquarters: str | None = None
    skill_level: int | None = Field(default=1, ge=1, le=10)


# Model


class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    users: list["User"] = Relationship(back_populates="team")


# Create


class TeamCreate(TeamBase):
    pass


# Read


class TeamPublic(TeamBase):
    id: uuid.UUID


class TeamPublicWithUsers(TeamPublic):
    users: list["UserPublic"] = []


# Update


class TeamUpdate(TeamBase):
    name: str | None = None
    skill_level: int | None = Field(default=None, ge=1, le=10)
