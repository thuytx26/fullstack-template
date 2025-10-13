from fastapi import FastAPI


from contextlib import asynccontextmanager


from app.api.main import api_router

from app.models.team_model import (
    Team,
)

from app.models.user_model import (
    User,
)


app = FastAPI()


app.include_router(api_router)