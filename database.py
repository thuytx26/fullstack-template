from sqlmodel import SQLModel, create_engine, Session


database_name = "database.db"
database_url = f"sqlite:///{database_name}"
engine = create_engine(database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

