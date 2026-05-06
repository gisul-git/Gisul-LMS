from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_verified_user, require_instructor
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter(
    prefix="/instructor", tags=["Instructor"], dependencies=[require_instructor]
)


@router.get("/dashboard")
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_verified_user)],
) -> SuccessResponse[dict]:
    """Instructor dashboard — placeholder."""
    return SuccessResponse(
        message="Instructor dashboard",
        data={
            "user": current_user.to_safe_dict(),
            "courses": [],
            "students": [],
        },
    )
