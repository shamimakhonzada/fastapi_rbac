from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: Optional[str] = None
    provider: Optional[str] = None
    provider_id: Optional[str] = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
