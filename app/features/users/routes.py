from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.put("/{user_id}", response_model=StandardResponse[UserResponse])
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
    "/{user_id}",
)
async def update_password(
    user_id: int, new_password: ChangePassword, db: Session = Depends(get_db)
):
    user = change_user_password(db, user_id, new_password.password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(message="Password updated successfully")


@router.get("/me/profile")
async def my_profile(current_user: User = Depends(get_current_user)):
    return success_response(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "full_name": current_user.full_name,
        },
        message="Profile retrieved successfully",
    )
