from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
import uuid

if TYPE_CHECKING:
    from ..models.team_model import Team, TeamPublic


# Base model

class UserBase(SQLModel):
    name: str = Field(index=True, unique=True, max_length=255)
    secret_name: str | None = Field(default=None)
    age: int | None = Field(default=None, index=True)
    money: Decimal = Field(default=0, max_digits=5, decimal_places=3)
    team_id: uuid.UUID | None = Field(default=None, foreign_key="team.id")


# Table model

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="users")
    hashed_password: str


# Create

class UserCreate(UserBase):
    hashed_password : str = Field(min_length=8, max_length=40)

class UserRegister(SQLModel):
    name: str = Field(max_length=255)
    hashed_password: str = Field(min_length=8, max_length=40)


# Read

class UserPublic(UserBase):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class UserPublicWithTeam(UserPublic):
    team: Optional["TeamPublic"] = None


#update

class UserUpdate(UserBase):
    name: str = Field(default=None, max_length=255)
    hashed_password : str = Field(default=None, min_length=8, max_length=40)