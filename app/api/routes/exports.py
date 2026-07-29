from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_container
from app.container import Container


router = APIRouter(
    prefix="/exports",
    tags=["exports"],
)


@router.get("/monthly.xlsx")
def export_monthly_excel(
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
    container: Container = Depends(get_container),
) -> StreamingResponse:
    content, filename = (
        container.monthly_export_service.build(
            year=year,
            month=month,
        )
    )

    return StreamingResponse(
        BytesIO(content),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )
