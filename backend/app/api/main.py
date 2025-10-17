from fastapi import APIRouter

from app.api.routers import login, teams, users

api_router = APIRouter()


api_router.include_router(teams.router)
api_router.include_router(users.router)
api_router.include_router(login.router)
