from dataclasses import dataclass
from datetime import date, datetime

from app.domain.money import MoneyInput
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)


@dataclass
class ExpenseCreate:
    purchase_date: datetime
    purchase_place: str
    purchase_value: MoneyInput
    category: str
    payment_method: str
    is_installment: bool = False
    installments: int = 1
    first_installment_due_date: date | None = None
    is_shared: bool = False
    shared_people: tuple[SharedPersonCreate, ...] = ()
    notes: str | None = None
