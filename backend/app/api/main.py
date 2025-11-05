from fastapi import APIRouter

from app.api.routers import login, private, teams, users
from app.core.config import settings

api_router = APIRouter()


api_router.include_router(teams.router)
api_router.include_router(users.router)
api_router.include_router(login.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
