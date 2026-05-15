from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.common.enums.user_role import UserRole
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    profile_image = Column(String, nullable=True)
    profile_image_public_id = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password = Column("hashed_password", String, nullable=True)
    role = Column(String, default=UserRole.USER.value)

    provider = Column(String, nullable=True)
    provider_id = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
