from fastapi import APIRouter

from app.api.routers import login, private, teams, users, utils
from app.core.config import settings

api_router = APIRouter()


api_router.include_router(teams.router)
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(utils.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
