from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.common.responses.response_builder import success_response
from app.common.responses.standard_response import StandardResponse
from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.oauth import oauth
from app.features.auth.repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_user_oauth,
)
from app.features.auth.schema import LoginSchema, RegisterSchema
from app.features.auth.service import (
    authenticate_user,
    build_access_token,
    register_user,
)
from app.features.users.model import User
from app.features.users.schema import UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


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


@router.get("/me", response_model=StandardResponse[UserResponse])
async def my_profile(
    current_user: User = Depends(get_current_user),
):

    return success_response(
        data=current_user,
        message="Profile retrieved successfully",
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return success_response(message="Logout successful")


@router.get("/google/login")
async def google_login(request: Request):

    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        prompt="select_account consent",
    )


@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):

    # exchange access token
    token = await oauth.google.authorize_access_token(request)

    # fetch google user info
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch user info from Google",
        )

    email = user_info.get("email")
    name = user_info.get("name")
    google_picture = user_info.get("picture")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account email not available",
        )

    # check existing user
    user = get_user_by_email(db, email)

    if not user:
        # create new user — handle potential username collision
        base_username = email.split("@")[0]
        username = base_username
        suffix = 1
        while get_user_by_username(db, username):
            username = f"{base_username}{suffix}"
            suffix += 1

        user_data = RegisterSchema(
            username=username,
            email=email,
            full_name=name or "Google User",
            provider="google",
            provider_id=user_info.get("sub"),
        )
        user = create_user(db, user_data)
        if not user.profile_image:
            user.profile_image = google_picture

        db.commit()
        db.refresh(user)

    else:
        # existing user — link Google account if not already linked
        if not user.provider:
            user = update_user_oauth(db, user, "google", user_info.get("sub"))

    # create YOUR jwt
    access_token = build_access_token(user)

    # redirect to frontend with cookie set
    redirect = RedirectResponse(url=settings.FRONTEND_URL)
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production HTTPS
        samesite="lax",
        max_age=3600,
    )
    return redirect
