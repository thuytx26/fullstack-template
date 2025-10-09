from sqlmodel import Session, select


from app.models.hero_model import Hero, HeroPublic

def get_hero_from_username(session: Session, username: str) -> Hero | None:
    statement = select(Hero).where(Hero.name == username)
    hero = session.exec(statement).first()
    return hero

