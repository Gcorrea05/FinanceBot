from dataclasses import dataclass

from app.database.models import Expense
from app.repositories.expense_repository import (
    ExpenseRepository,
)


class ExpenseNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class ExpensePage:
    items: list[Expense]
    total: int
    limit: int
    offset: int


class ExpenseManagementService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
    ):
        self.expense_repository = (
            expense_repository
        )

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        month: int | None = None,
        year: int | None = None,
    ) -> ExpensePage:
        items = (
            self.expense_repository
            .list_filtered(
                limit=limit,
                offset=offset,
                month=month,
                year=year,
            )
        )

        total = (
            self.expense_repository
            .count_filtered(
                month=month,
                year=year,
            )
        )

        return ExpensePage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get(
        self,
        expense_id: int,
    ) -> Expense:
        expense = (
            self.expense_repository
            .get_detailed_by_id(
                expense_id
            )
        )

        if expense is None:
            raise ExpenseNotFoundError(
                (
                    f"Expense {expense_id} "
                    "was not found."
                )
            )

        return expense

    def delete(
        self,
        expense_id: int,
    ) -> None:
        deleted = (
            self.expense_repository
            .delete_by_id(expense_id)
        )

        if not deleted:
            raise ExpenseNotFoundError(
                (
                    f"Expense {expense_id} "
                    "was not found."
                )
            )
