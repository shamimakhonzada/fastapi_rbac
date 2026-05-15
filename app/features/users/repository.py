from sqlalchemy.orm import Session

from app.features.users.model import User
from app.features.users.schema import UpdateUser


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def update_user(db: Session, user: User, user_update: UpdateUser) -> User:
    user.username = user_update.username if user_update.username else user.username
    user.role = user_update.role if user_update.role else user.role
    user.full_name = user_update.full_name if user_update.full_name else user.full_name
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: User, password: str) -> User:
    user.password = password
    db.commit()
    db.refresh(user)
    return user
