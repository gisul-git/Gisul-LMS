from typing import Any, Optional

from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse, SuccessResponse


def success(message: str, data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=SuccessResponse(message=message, data=data).model_dump(),
    )


def error(message: str, code: Optional[str] = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(message=message, code=code).model_dump(),
    )
