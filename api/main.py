from fastapi import FastAPI

from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .routers.heroes import router as hero_router
from .routers.teams import router as team_router


from .models.team_model import (
    Team,
)

from .models.hero_model import (
    Hero,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    pass


app = FastAPI(lifespan=lifespan)


app.include_router(team_router)
app.include_router(hero_router)