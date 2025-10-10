from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlmodel import select, Session


from app.api.deps import (
    SessionDep, 
    TokenDep, 
    CurrentUserDep,
)

from app.models.user_model import (
    User,
    # UserBase,
    UserCreate,
    UserPublic,
    UserUpdate,
    UserPublicWithTeam,
)

from app.models.team_model import Team
from app.core.security import get_password_hash
from app.utils import crud



router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserPublicWithTeam)
async def read_users_me(
    current_user: CurrentUserDep,
):
    return current_user

# Create

@router.post("/", response_model=UserPublic)
def create_user(
    *, 
    session: SessionDep,
    user_in: UserCreate, 
):
    
    db_user = crud.get_user_from_username(
        session, 
        user_in.name
    )
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="User already exists"
        )
    
    user = crud.create_user(
        session,
        user_in,
    )
    
    return user


@router.get("/{user_id}", response_model=UserPublicWithTeam)
def read_user(
    *, 
    user_id: uuid.UUID, 
    session: SessionDep
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserPublic])
def read_users(
    *, 
    session: SessionDep, 
    offset: int = 0, 
    limit: int = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *, 
    user_id: uuid.UUID,
    user: UserUpdate, 
    session: SessionDep
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=UserPublic)
def delete_user(
    *,
    user_id: uuid.UUID, 
    session: SessionDep
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user