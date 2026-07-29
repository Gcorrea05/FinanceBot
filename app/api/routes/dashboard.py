from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_container
from app.api.schemas.dashboard import (
    DashboardComparisonResponse,
    DashboardDailyPointResponse,
    DashboardOverviewResponse,
)
from app.api.schemas.report import CategoryReportResponse
from app.api.serializers import serialize_expense
from app.container import Container

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def dashboard_overview(
    year: int = Query(ge=2000),
    month: int = Query(ge=1, le=12),
    container: Container = Depends(get_container),
) -> DashboardOverviewResponse:
    result = container.dashboard_service.get_overview(
        year=year,
        month=month,
    )
    return DashboardOverviewResponse(
        year=result.year,
        month=result.month,
        spent=result.spent,
        planned_income=result.planned_income,
        reserve_target=result.reserve_target,
        budget_remaining=result.budget_remaining,
        budget_status=result.budget_status,
        receivables=result.receivables,
        forecast_total=result.forecast_total,
        comparison=DashboardComparisonResponse(
            previous_month_total=result.comparison.previous_month_total,
            previous_month_change_percent=(
                result.comparison.previous_month_change_percent
            ),
            year_ago_total=result.comparison.year_ago_total,
            year_ago_change_percent=(
                result.comparison.year_ago_change_percent
            ),
        ),
        categories=[
            CategoryReportResponse(
                name=item.name,
                total=item.total,
                percentage=item.percentage,
            )
            for item in result.categories
        ],
        daily=[
            DashboardDailyPointResponse(day=item.day, total=item.total)
            for item in result.daily
        ],
        recent_expenses=[
            serialize_expense(expense)
            for expense in result.recent_expenses
        ],
    )
