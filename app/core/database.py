from sqlmodel import SQLModel, create_engine


database_name = "database.db"
database_url = f"sqlite:///{database_name}"
engine = create_engine(database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

