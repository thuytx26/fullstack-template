from fastapi import FastAPI


from contextlib import asynccontextmanager

from app.core.database import create_db_and_tables

from app.api.main import api_router

from app.models.team_model import (
    Team,
)

from app.models.hero_model import (
    Hero,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    pass


app = FastAPI(lifespan=lifespan)


app.include_router(api_router)