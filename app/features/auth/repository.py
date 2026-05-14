from sqlalchemy.orm import Session

from app.common.enums.user_role import UserRole
from app.features.users.model import User
from app.features.auth.schema import RegisterSchema


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def update_user_oauth(db: Session, user: User, provider: str, provider_id: str) -> User:
    user.provider = provider
    user.provider_id = provider_id
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, user_data: RegisterSchema) -> User:
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password,  # None for OAuth users
        role=UserRole.USER,
        provider=user_data.provider,
        provider_id=user_data.provider_id,
        is_verified=user_data.provider is not None,  # OAuth users are pre-verified
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
