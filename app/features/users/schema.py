from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str


class UpdateUser(BaseModel):
    username: str | None = None
    full_name: str | None = None
    role: str | None = None


class ChangePassword(BaseModel):
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    profile_image: str | None = None
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
