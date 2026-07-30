from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_container
from app.api.schemas.future import FutureMonthResponse, FutureOverviewResponse
from app.container import Container

router = APIRouter(prefix="/future", tags=["future"])


@router.get("/overview", response_model=FutureOverviewResponse)
def get_future_overview(
    from_year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100),
    from_month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12),
    months: int = Query(12, ge=1, le=36),
    container: Container = Depends(get_container),
) -> FutureOverviewResponse:
    container.recurring_expense_service.materialize(
        from_year=from_year, from_month=from_month, months=months
    )
    items = container.future_planning_service.overview(
        from_year=from_year, from_month=from_month, months=months
    )
    return FutureOverviewResponse(
        items=[FutureMonthResponse(**item.__dict__) for item in items]
    )
