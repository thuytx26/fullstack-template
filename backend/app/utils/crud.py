from sqlmodel import Session, select
from fastapi.exceptions import HTTPException
from fastapi import status

from app.models.user_model import (
    User, 

    UserCreate,
    UserRegister,

    UserPublic,
    
    UserUpdate,
    UserUpdateMe,
    UserUpdatePassword,
)

from app.models.team_model import (
    Team
)

from app.core.security import (
    get_password_hash,
    verify_password,
)


def get_user_from_username(
    session: Session, 
    username: str
) -> User | None:
    statement = select(User).where(User.name == username)
    user = session.exec(statement).first()
    return user


def create_user(
    session: Session, 
    user_create: UserCreate
) -> User:
    
    db_obj = User.model_validate(
        user_create, 
        update = {"hashed_password" : get_password_hash(user_create.password)}
    )

    if db_obj.team_id:
        team = session.get(Team, db_obj.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Team not found"
                )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def register_user(
    session: Session, 
    user_register: UserRegister
) -> User:
    db_obj = User.model_validate(
        user_register, 
        update = {"hashed_password" : get_password_hash(user_register.password)}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
        


def update_user(
    session: Session,
    db_user: User,
    user_in: UserUpdate,
) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    user_extras = {}

    if user_in.password:
        user_extras["hashed_password"] = get_password_hash(user_in.password)

    db_user.sqlmodel_update(user_data, update=user_extras)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user_me(
    session: Session,
    db_user: User,
    user_in: UserUpdateMe,
):
    user_data = user_in.model_dump(exclude_unset=True)
    
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_password(
    session: Session,
    db_user: User,
    update_password: UserUpdatePassword,
):
    db_user.hashed_password = get_password_hash(update_password.new_password)

    session.add(db_user)
    session.commit()