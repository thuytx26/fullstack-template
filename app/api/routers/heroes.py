from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlmodel import select, Session


from app.api.deps import (
    SessionDep, 
    TokenDep, 
    CurrentUserDep,
)

from app.models.hero_model import (
    Hero,
    # HeroBase,
    HeroCreate,
    HeroPublic,
    HeroUpdate,
    HeroPublicWithTeam,
)

from app.models.team_model import Team
from app.core.security import get_password_hash
from app.utils import crud



router = APIRouter(
    prefix="/heroes",
    tags=["heroes"],
)


@router.get("/me", response_model=HeroPublic)
async def read_users_me(
    current_user: CurrentUserDep,
):
    return current_user



@router.post("/", response_model=HeroPublic)
def create_hero(*, hero: HeroCreate, 
                session: SessionDep,
                ):
    # check if hero exits
    db_hero = crud.get_hero_from_username(session, hero.name)
    if db_hero:
        raise HTTPException(
            status_code=400, 
            detail="Hero already exists"
        )

    db_hero = Hero.model_validate(
        hero, 
        update = {"hashed_password" : get_password_hash(hero.password)}
    )

    # check team_id exists
    if db_hero.team_id:
        team = session.get(Team, db_hero.team_id)
        if not team:
            raise HTTPException(status_code=400, detail="Team not found")

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("/{hero_id}", response_model=HeroPublicWithTeam)
def read_hero(
    *, 
    hero_id: uuid.UUID, 
    session: SessionDep
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.get("/", response_model=list[HeroPublic])
def read_heroes(
    *, 
    session: SessionDep, 
    offset: int = 0, 
    limit: int = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@router.patch("/{hero_id}", response_model=HeroPublic)
def update_hero(
    *, 
    hero_id: uuid.UUID,
    hero: HeroUpdate, 
    session: SessionDep
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.delete("/{hero_id}", response_model=HeroPublic)
def delete_hero(
    *,
    hero_id: uuid.UUID, 
    session: SessionDep
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return hero