from sqlmodel import Session, select

import uuid

from .models.team_model import (
    Team,
    TeamCreate,
    TeamPublic,
    TeamUpdate,
    TeamPublicWithHeroes,
)


from .models.hero_model import (
    Hero,
    HeroCreate,
    HeroPublic,
    HeroUpdate,
    HeroPublicWithTeam,
)


from .database import create_db_and_tables, get_session

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,

)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    pass


app = FastAPI(lifespan=lifespan)


@app.post("/teams/", response_model=TeamPublic)
def create_team(*, team: TeamCreate, session: Session = Depends(get_session)):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team
    

@app.get("/teams/{team_id}", response_model=TeamPublicWithHeroes)
def read_team(*, team_id: uuid.UUID, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.get("/teams/", response_model=list[TeamPublic])
def read_teams(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams


@app.patch("/teams/{team_id}", response_model=TeamPublic)
def update_team(*, team_id: uuid.UUID, team: TeamUpdate, session: Session = Depends(get_session)):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@app.delete("/teams/{team_id}", response_model=TeamPublic)
def delete_team(*, team_id: uuid.UUID, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return team


@app.post("/heroes/", response_model=HeroPublic)
def create_hero(*, hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)

    # check team_id exists
    if db_hero.team_id:
        team = session.get(Team, db_hero.team_id)
        if not team:
            raise HTTPException(status_code=400, detail="Team not found")

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/{hero_id}", response_model=HeroPublicWithTeam)
def read_hero(*, hero_id: uuid.UUID, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    *, 
    session: Session = Depends(get_session), 
    offset: int = 0, 
    limit: int = 100):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(
    *, 
    hero_id: uuid.UUID,
    hero: HeroUpdate, 
    session: Session = Depends(get_session)
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


@app.delete("/heroes/{hero_id}", response_model=HeroPublic)
def delete_hero(*, hero_id: uuid.UUID, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return hero

