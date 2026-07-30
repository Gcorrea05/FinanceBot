from decimal import Decimal
from pydantic import BaseModel


class FutureMonthResponse(BaseModel):
    year: int
    month: int
    recorded_total: Decimal
    installment_total: Decimal
    recurring_total: Decimal
    committed_total: Decimal
    monthly_income: Decimal | None
    reserve_target: Decimal | None
    spending_limit: Decimal | None
    available_to_spend: Decimal | None
    status: str


class FutureOverviewResponse(BaseModel):
    items: list[FutureMonthResponse]
