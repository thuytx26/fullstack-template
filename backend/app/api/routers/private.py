from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from app.api.deps import SessionDep
from app.models.user_model import UserCreate, UserPublic
from app.utils import crud

router = APIRouter(
    prefix="/private",
    tags=["private"],
)


@router.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user_private(
    session: SessionDep,
    user_in: UserCreate,
):
    db_user = crud.get_user_from_username(session, user_in.name)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists",
        )

    user = crud.create_user(
        session=session,
        user_create=user_in,
    )

    return user
