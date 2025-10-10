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


@router.get("/me", response_model=HeroPublicWithTeam)
async def read_users_me(
    current_user: CurrentUserDep,
):
    return current_user

# Create

@router.post("/", response_model=HeroPublic)
def create_hero(
    *, 
    session: SessionDep,
    hero_in: HeroCreate, 
):
    
    db_hero = crud.get_hero_from_username(
        session, 
        hero_in.name
    )
    if db_hero:
        raise HTTPException(
            status_code=400, 
            detail="Hero already exists"
        )
    
    hero = crud.create_user(
        session,
        hero_in,
    )
    
    return hero


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