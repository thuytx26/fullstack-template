from sqlmodel import Session

from app.utils.crud import (
    get_user_from_username,
)

from app.core.security import verify_password


def authentication(
    session: Session, 
    username: str, 
    password: str,
):
    user = get_user_from_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None  
    return user

