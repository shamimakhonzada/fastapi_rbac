from sqlalchemy.orm import Session

from app.features.auth.repository import create_user, get_user_by_email
from app.features.auth.schema import RegisterSchema
from app.features.auth.utils import create_access_token, hash_password, verify_password
from app.features.users.model import User


def register_user(db: Session, user_data: RegisterSchema) -> User:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        return None

    hashed_password = hash_password(user_data.password)
    user_data.password = hashed_password
    return create_user(db, user_data)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def build_access_token(user: User) -> str:
    return create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "id": user.id,
        }
    )
