from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class BudgetPlanRequest(BaseModel):
    monthly_income: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    reserve_target: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    spending_limit: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    repeat_months: int = Field(
        default=1,
        ge=1,
        le=36,
    )


class BudgetOverviewResponse(BaseModel):
    year: int
    month: int
    configured: bool
    monthly_income: Decimal | None
    reserve_target: Decimal | None
    spending_limit: Decimal | None
    spent: Decimal
    remaining: Decimal | None
    available_after_reserve: Decimal | None
    daily_limit: Decimal | None
    usage_percent: Decimal | None
    remaining_days: int
    status: str
