from sqlmodel import Session, select
from fastapi.exceptions import HTTPException

from app.models.hero_model import (
    Hero, 
    HeroPublic,
    HeroCreate
)

from app.models.team_model import (
    Team
)

from app.core.security import get_password_hash




def get_hero_from_username(
        session: Session, 
        username: str
) -> Hero | None:
    statement = select(Hero).where(Hero.name == username)
    hero = session.exec(statement).first()
    return hero


def create_user(
        session: Session, 
        hero_create: HeroCreate
) -> Hero:
    
    db_obj = Hero.model_validate(
        hero_create, 
        update = {"hashed_password" : get_password_hash(hero_create.password)}
    )

    if db_obj.team_id:
        team = session.get(Team, db_obj.team_id)
        if not team:
            raise HTTPException(status_code=400, detail="Team not found")

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj