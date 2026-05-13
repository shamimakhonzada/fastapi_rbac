from sqlalchemy.orm import Session

from app.common.enums.user_role import UserRole
from app.features.users.model import User
from app.features.auth.schema import RegisterSchema


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: RegisterSchema) -> User:
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password,
        role=UserRole.USER,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
