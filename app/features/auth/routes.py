from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.common.responses.response_builder import success_response
from app.core.dependencies import get_db
from app.features.auth.schema import LoginSchema, RegisterSchema
from app.features.auth.service import (
    build_access_token,
    register_user,
    authenticate_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(user_data: RegisterSchema, db: Session = Depends(get_db)):
    new_user = register_user(db, user_data)
    if new_user is None:
        raise HTTPException(status_code=400, detail="Email already registered")

    return success_response(
        message="Registration successful",
    )


@router.post("/login")
async def login(
    user_credentials: LoginSchema, response: Response, db: Session = Depends(get_db)
):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = build_access_token(user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="lax",
        secure=False,
    )

    return success_response(
        message="Login successful",
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return success_response(message="Logout successful")
