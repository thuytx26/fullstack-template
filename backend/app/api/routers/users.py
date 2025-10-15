from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status,
)
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
    get_current_superuser,
)
from app.models.user_model import (
    User,
    UserCreate,
    UserRegister,
    UserPublic,
    UsersPublic,
    UserPublicWithTeam,
    UserUpdate,
    UserUpdateMe,
    UserUpdatePassword,
)
from app.models.utils_model import Message
from app.models.team_model import Team
from app.core.security import get_password_hash
from app.utils import crud
from app.core.security import verify_password


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/signup",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    *,
    session: SessionDep,
    user_in: UserRegister,
):
    db_user = crud.get_user_from_username(session, user_in.name)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists",
        )

    user = crud.register_user(
        session,
        user_in,
    )
    return user


@router.get("/me", response_model=UserPublicWithTeam)
async def read_user_me(
    current_user: CurrentUserDep,
):
    return current_user


@router.patch(
    "/me", 
    response_model=UserPublic,
)
def update_user_me(
    *, 
    session: SessionDep,
    user_in: UserUpdateMe, 
    current_user: CurrentUserDep,
):
    if user_in.name:
        existing_user = crud.get_user_from_username(
            session, 
            user_in.name
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this name already exists",
            )

    if user_in.team_id:
        team = session.get(Team, user_in.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Team not found"
            )

    updated_user = crud.update_user_me(
        session=session,
        db_user=current_user,
        user_in=user_in,
    )
    
    return updated_user


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def update_user_password(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    update_password: UserUpdatePassword,
):
    # verify password
    if not verify_password(
        plain_password=update_password.old_password, 
        hashed_password=current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    crud.update_password(
        session=session,
        db_user=current_user,
        update_password=update_password,
    )

    return Message(message="Password updated successfully")


@router.delete(
    "/me", 
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUserDep, 
):
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(current_user)
    session.commit()


@router.get(
    "/", 
    dependencies=[Depends(get_current_superuser)],
    response_model=UsersPublic
)
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


@router.post(
    "/", 
    response_model=UserPublic, 
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_201_CREATED,
)
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
            status_code=status.HTTP_409_CONFLICT, 
            detail="User with this name already exists"
        )
    
    user = crud.create_user(
        session,
        user_in,
    )
    
    return user


@router.get(
    "/{user_id}",
    response_model=UserPublicWithTeam,
)
def read_user(
    *, 
    session: SessionDep,
    user_id: uuid.UUID, 
    current_user: CurrentUserDep,
):
    user = session.get(User, user_id)

    if current_user.is_superuser:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user with this id doesn't exist in the system",
            )
        return user

    # For regular users:
    # Only return a successful response if the user exists AND it is the user themselves.
    # In ALL other cases (user does not exist, or user is another user),
    # return a 404 error to prevent user enumeration attacks.
    if user and user.id == current_user.id:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )


@router.patch(
    "/{user_id}", 
    dependencies=[Depends(get_current_superuser)],
    response_model=UserPublic,
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
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    if user_in.name:
        existing_user = crud.get_user_from_username(
            session, 
            user_in.name
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="User with this name already exists"
            )
    
    if user_in.team_id:
        team = session.get(Team, user_in.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Team not found"
            )

    db_user = crud.update_user(
        session,
        db_user,
        user_in,
    )
    return db_user


@router.delete(
    "/{user_id}", 
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID, 
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(user)
    session.commit()