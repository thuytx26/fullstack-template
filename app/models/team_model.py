from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid


if TYPE_CHECKING:
    from ..models.hero_model import Hero, HeroPublic

class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str | None = None


class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    heroes: list["Hero"] = Relationship(back_populates="team")
    

class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: uuid.UUID


class TeamPublicWithHeroes(TeamPublic):
    heroes: list["HeroPublic"] = []

class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None
