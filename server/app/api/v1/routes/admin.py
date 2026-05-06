from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import (
    get_current_verified_user,
    get_user_service,
    require_admin,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.user import UpdateUserRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[require_admin])


@router.get("/dashboard")
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SuccessResponse[dict]:
    """Admin dashboard with platform overview."""
    total_users = await user_service.count()
    return SuccessResponse(
        message="Admin dashboard",
        data={
            "user": current_user.to_safe_dict(),
            "stats": {"total_users": total_users},
        },
    )


@router.get("/users")
async def list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    """List all users with pagination."""
    skip = (page - 1) * page_size
    users = await user_service.list_users(skip=skip, limit=page_size)
    total = await user_service.count()

    return PaginatedResponse(
        data=[
            UserResponse(
                id=str(u.id),
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                is_active=u.is_active,
                email_verified=u.email_verified,
                created_at=u.created_at,
                last_login_at=u.last_login_at,
            )
            for u in users
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SuccessResponse[UserResponse]:
    """Update user details (admin only)."""
    user = await user_service.update(user_id, data)
    return SuccessResponse(
        message="User updated",
        data=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        ),
    )
