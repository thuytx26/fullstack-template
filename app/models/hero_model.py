from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
import uuid

if TYPE_CHECKING:
    from ..models.team_model import Team, TeamPublic


# Base model

class HeroBase(SQLModel):
    name: str = Field(index=True, unique=True, max_length=255)
    secret_name: str | None = Field(default=None)
    age: int | None = Field(default=None, index=True)
    money: Decimal = Field(default=0, max_digits=5, decimal_places=3)
    team_id: uuid.UUID | None = Field(default=None, foreign_key="team.id")


# Table model

class Hero(HeroBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="heroes")
    hashed_password: str


# Create

class HeroCreate(HeroBase):
    password : str = Field(min_length=8, max_length=40)

class HeroRegister(SQLModel):
    name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


# Read

class HeroPublic(HeroBase):
    id: uuid.UUID

class HeroPublicWithTeam(HeroPublic):
    team: Optional["TeamPublic"] = None


#update

class HeroUpdate(HeroBase):
    name: str = Field(default=None, max_length=255)