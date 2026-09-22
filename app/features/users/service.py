from sqlalchemy.orm import Session

from app.features.auth.utils import hash_password
from app.features.users.model import User
from app.features.users.repository import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
    update_user_password,
)
from app.features.users.schema import UpdateUser


def list_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    return get_all_users(db, skip=skip, limit=limit)


def get_user(db: Session, user_id: int) -> User | None:
    return get_user_by_id(db, user_id)


def update_existing_user(
    db: Session, user_id: int, user_update: UpdateUser
) -> User | None:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    return update_user(db, user, user_update)


def delete_existing_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user is None:
        return False
    delete_user(db, user)
    return True


def change_user_password(db: Session, user_id: int, new_password: str) -> User | None:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    hashed_password = hash_password(new_password)
    return update_user_password(db, user, hashed_password)
