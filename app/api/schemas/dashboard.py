from decimal import Decimal

from pydantic import BaseModel

from app.api.schemas.expense import ExpenseResponse
from app.api.schemas.report import CategoryReportResponse


class DashboardComparisonResponse(BaseModel):
    previous_month_total: Decimal
    previous_month_change_percent: Decimal | None
    year_ago_total: Decimal
    year_ago_change_percent: Decimal | None


class DashboardDailyPointResponse(BaseModel):
    day: int
    total: Decimal


class DashboardOverviewResponse(BaseModel):
    year: int
    month: int
    spent: Decimal
    planned_income: Decimal | None
    reserve_target: Decimal | None
    budget_remaining: Decimal | None
    budget_status: str
    receivables: Decimal
    forecast_total: Decimal
    comparison: DashboardComparisonResponse
    categories: list[CategoryReportResponse]
    daily: list[DashboardDailyPointResponse]
    recent_expenses: list[ExpenseResponse]
