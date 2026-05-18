from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary.uploader

from app.core import cloudinary_config

from app.common.enums.user_role import UserRole
from app.common.responses.response_builder import success_response
from app.common.responses.standard_response import StandardResponse
from app.common.utils.permissions import require_roles
from app.core.dependencies import get_db
from app.core.dependencies import get_current_user
from app.features.users.schema import ChangePassword, UpdateUser, UserResponse
from app.features.users.service import (
    change_user_password,
    delete_existing_user,
    get_user,
    list_users,
    update_existing_user,
)
from app.features.users.model import User

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/", response_model=StandardResponse[list[UserResponse]])
async def get_users(
    db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))
):
    users = list_users(db)
    return success_response(data=users, message="Users retrieved successfully")


@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        data=user, message=f"User with ID {user_id} retrieved successfully"
    )


@router.patch("/{user_id}", response_model=StandardResponse[UserResponse])
async def update_user(
    user_id: int,
    user_update: UpdateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="You do not have permission to update other users"
        )

    if current_user.role == UserRole.ADMIN:
        updated_user = update_existing_user(db, user_id, user_update)

    elif current_user.role != UserRole.ADMIN and current_user.id == user_id:
        if user_update.role and user_update.role != current_user.role:
            raise HTTPException(
                status_code=403, detail="You cannot change your own role"
            )
        updated_user = update_existing_user(db, user_id, user_update)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        data=updated_user, message=f"User with ID {user_id} updated successfully"
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    deleted = delete_existing_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(message="User deleted successfully")


@router.patch(
    "/{user_id}/change-password",
)
async def update_password(
    user_id: int, new_password: ChangePassword, db: Session = Depends(get_db)
):
    user = change_user_password(db, user_id, new_password.password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(message="Password updated successfully")


@router.get("/me/profile", response_model=StandardResponse[UserResponse])
async def my_profile(
    current_user: User = Depends(get_current_user),
):

    return success_response(
        data=current_user,
        message="Profile retrieved successfully",
    )


@router.post("/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, WEBP allowed",
        )

    MAX_FILE_SIZE = 5 * 1024 * 1024

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 5MB",
        )

    file.file.seek(0)

    # delete old image if exists
    if current_user.profile_image_public_id:
        cloudinary.uploader.destroy(current_user.profile_image_public_id)

    result = cloudinary.uploader.upload(
        file.file,
        folder=f"fastapi_rbac_profiles/{current_user.id}",
    )

    current_user.profile_image = result["secure_url"]

    current_user.profile_image_public_id = result["public_id"]

    db.commit()
    db.refresh(current_user)

    return success_response(
        message="Profile image uploaded successfully",
        data={
            "image_url": current_user.profile_image,
        },
    )
