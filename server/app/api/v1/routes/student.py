from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_verified_user, require_student
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/student", tags=["Student"], dependencies=[require_student])


@router.get("/dashboard")
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_verified_user)],
) -> SuccessResponse[dict]:
    """Student dashboard — placeholder."""
    return SuccessResponse(
        message="Student dashboard",
        data={
            "user": current_user.to_safe_dict(),
            "courses": [],
            "assignments": [],
        },
    )
