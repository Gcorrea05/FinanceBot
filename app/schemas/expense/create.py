from dataclasses import dataclass
from datetime import datetime

from app.domain.money import MoneyInput


@dataclass
class ExpenseCreate:
    purchase_date: datetime
    purchase_place: str
    purchase_value: MoneyInput
    category: str
    payment_method: str
    is_installment: bool = False
    installments: int = 1
    is_shared: bool = False
    notes: str | None = None
