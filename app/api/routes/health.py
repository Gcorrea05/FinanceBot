from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_session_dependency,
)
from app.api.schemas.common import StatusResponse


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get(
    "/live",
    response_model=StatusResponse,
)
def live() -> StatusResponse:
    return StatusResponse(
        status="ok",
    )


@router.get(
    "/ready",
    response_model=StatusResponse,
)
def ready(
    session: Session = Depends(
        get_session_dependency
    ),
) -> StatusResponse:
    try:
        session.execute(
            text("SELECT 1")
        )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready.",
        ) from error

    return StatusResponse(
        status="ready",
    )
