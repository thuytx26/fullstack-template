from sqlmodel import create_engine, Session, SQLModel

from app.models.user_model import UserCreate
from app.core.config import settings
from app.utils import crud


database_url = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_engine(database_url, echo=True)


def init_db(session: Session):
    db_user = crud.get_user_from_username(
        session = session,
        username = settings.FIRST_SUPERUSER_NAME,
    )
    if not db_user:
        crud.create_user(
            session = session,
            user_create = UserCreate(
                name = settings.FIRST_SUPERUSER_NAME,
                password = settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser = True,
            )
        )