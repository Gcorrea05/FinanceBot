from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.database.models import Expense
from app.repositories.base_repository import BaseRepository


class ExpenseRepository(
    BaseRepository[Expense]
):
    MAX_QUERY_LIMIT = 50

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(session)

    @staticmethod
    def _detailed_statement():
        return select(Expense).options(
            selectinload(Expense.category),
            selectinload(
                Expense.payment_method
            ),
        )

    def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:
        return self.session.get(
            Expense,
            expense_id,
        )

    def get_all(
        self,
    ) -> list[Expense]:
        statement = (
            self._detailed_statement()
            .order_by(
                Expense.purchase_date.desc(),
                Expense.id.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def list_recent(
        self,
        limit: int = 5,
    ) -> list[Expense]:
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
        ):
            raise ValueError(
                "O limite deve ser um inteiro positivo."
            )

        safe_limit = min(
            limit,
            self.MAX_QUERY_LIMIT,
        )

        statement = (
            self._detailed_statement()
            .order_by(
                Expense.purchase_date.desc(),
                Expense.id.desc(),
            )
            .limit(safe_limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def get_current_month(
        self,
        month: int,
        year: int,
    ) -> list[Expense]:
        if (
            isinstance(month, bool)
            or not isinstance(month, int)
            or not 1 <= month <= 12
        ):
            raise ValueError(
                "O mes deve estar entre 1 e 12."
            )

        if (
            isinstance(year, bool)
            or not isinstance(year, int)
            or year < 1
        ):
            raise ValueError(
                "O ano deve ser um inteiro positivo."
            )

        start = datetime(
            year,
            month,
            1,
        )

        if month == 12:
            end = datetime(
                year + 1,
                1,
                1,
            )
        else:
            end = datetime(
                year,
                month + 1,
                1,
            )

        statement = (
            self._detailed_statement()
            .where(
                Expense.purchase_date >= start,
                Expense.purchase_date < end,
            )
            .order_by(
                Expense.purchase_date.desc(),
                Expense.id.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )
