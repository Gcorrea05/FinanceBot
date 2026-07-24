from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.repositories.expense_repository import (
    ExpenseRepository,
)


@dataclass(frozen=True)
class RecentExpense:
    expense_id: int
    purchase_date: datetime
    purchase_place: str
    purchase_value: Decimal
    category_name: str
    payment_method_name: str
    is_installment: bool
    is_shared: bool


class ExpenseQueryService:
    CENT = Decimal("0.01")

    def __init__(
        self,
        expense_repository: ExpenseRepository,
    ):
        self.expense_repository = expense_repository

    def list_recent(
        self,
        limit: int = 5,
    ) -> list[RecentExpense]:
        expenses = (
            self.expense_repository
            .list_recent(limit=limit)
        )

        return [
            RecentExpense(
                expense_id=expense.id,
                purchase_date=(
                    expense.purchase_date
                ),
                purchase_place=(
                    expense.purchase_place
                ),
                purchase_value=self._money(
                    expense.purchase_value
                ),
                category_name=(
                    expense.category.name
                ),
                payment_method_name=(
                    expense.payment_method.name
                ),
                is_installment=(
                    expense.is_installment
                ),
                is_shared=expense.is_shared,
            )
            for expense in expenses
        ]

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:
        return Decimal(
            str(value)
        ).quantize(cls.CENT)
