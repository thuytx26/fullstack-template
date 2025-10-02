from fastapi import APIRouter


from app.api.routers import teams, heroes

api_router = APIRouter()


api_router.include_router(teams.router)
api_router.include_router(heroes.router)
