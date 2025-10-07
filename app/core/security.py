from datetime import datetime, timezone, timedelta
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


# password_hash = PasswordHash((Argon2Hasher(),))


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def verify_password(plain_password, hashed_password):
#     return password_hash.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return password_hash.hash(password)



