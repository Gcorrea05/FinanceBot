from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class RecurringExpenseResponse(BaseModel):
    id: int
    description: str
    amount: Decimal
    category: str
    payment_method: str
    due_day: int
    start_date: date
    end_date: date | None
    active: bool
    auto_post: bool


class RecurringExpenseUpdateRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    due_day: int = Field(ge=1, le=31)
    active: bool = True
    auto_post: bool = True
