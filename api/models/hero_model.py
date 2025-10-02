from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
import uuid

if TYPE_CHECKING:
    from ..models.team_model import Team, TeamPublic


class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    money: Decimal = Field(default=0, max_digits=5, decimal_places=3)

    team_id: uuid.UUID | None = Field(default=None, foreign_key="team.id")


class Hero(HeroBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    team: Optional["Team"] = Relationship(back_populates="heroes")


class HeroCreate(HeroBase):
    pass


class HeroPublic(HeroBase):
    id: uuid.UUID


class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: uuid.UUID | None = None


class HeroPublicWithTeam(HeroPublic):
    team: Optional["TeamPublic"] = None