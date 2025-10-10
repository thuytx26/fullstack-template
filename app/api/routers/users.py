from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlmodel import (
    select, 
    Session,
    func
)


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
    UsersPublic,
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
    session: SessionDep,
    user_id: uuid.UUID, 
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=UsersPublic)
def read_users(
    *, 
    session: SessionDep, 
    offset: int = 0, 
    limit: int = 100
):
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return UsersPublic(data=users, count=count)


@router.patch(
    "/{user_id}", 
    response_model=UserPublic
)
def update_user(
    *, 
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate, 
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404, 
            detail="User not found"
        )
    
    if user_in.name:
        existing_user = crud.get_user_from_username(
            session, 
            user_in.name
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400, 
                detail="User with this name is already exists"
            )
    
    if user_in.team_id:
        team = session.get(Team, user_in.team_id)
        if not team:
            raise HTTPException(
                status_code=400, 
                detail="Team not found"
            )

    db_user = crud.update_user(
        session,
        db_user,
        user_in,
    )
    return db_user


@router.delete("/{user_id}", response_model=UserPublic)
def delete_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID, 
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user