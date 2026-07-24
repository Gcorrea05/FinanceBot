from datetime import datetime

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.database.models import (
    Expense,
    ExpensePerson,
)
from app.repositories.base_repository import BaseRepository


class ExpenseRepository(
    BaseRepository[Expense]
):
    MAX_QUERY_LIMIT = 100

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
            selectinload(
                Expense.installments
            ),
            selectinload(
                Expense.people
            ).selectinload(
                ExpensePerson.person
            ),
        )

    @staticmethod
    def _period_bounds(
        month: int | None,
        year: int | None,
    ) -> tuple[
        datetime | None,
        datetime | None,
    ]:
        if month is not None:
            if year is None:
                raise ValueError(
                    (
                        "Year is required when "
                        "month is provided."
                    )
                )

            if (
                isinstance(month, bool)
                or not isinstance(month, int)
                or not 1 <= month <= 12
            ):
                raise ValueError(
                    (
                        "Month must be between "
                        "1 and 12."
                    )
                )

        if year is not None:
            if (
                isinstance(year, bool)
                or not isinstance(year, int)
                or year < 1
            ):
                raise ValueError(
                    (
                        "Year must be a positive "
                        "integer."
                    )
                )

        if year is None:
            return None, None

        if month is None:
            return (
                datetime(year, 1, 1),
                datetime(year + 1, 1, 1),
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

        return start, end

    def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:
        return self.session.get(
            Expense,
            expense_id,
        )

    def get_detailed_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:
        statement = (
            self._detailed_statement()
            .where(
                Expense.id == expense_id
            )
        )

        return self.session.scalar(
            statement
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
                (
                    "The limit must be a "
                    "positive integer."
                )
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

    def list_filtered(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        month: int | None = None,
        year: int | None = None,
    ) -> list[Expense]:
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= self.MAX_QUERY_LIMIT
        ):
            raise ValueError(
                (
                    "The limit must be between "
                    f"1 and {self.MAX_QUERY_LIMIT}."
                )
            )

        if (
            isinstance(offset, bool)
            or not isinstance(offset, int)
            or offset < 0
        ):
            raise ValueError(
                (
                    "The offset must be a "
                    "non-negative integer."
                )
            )

        start, end = self._period_bounds(
            month,
            year,
        )

        statement = (
            self._detailed_statement()
            .order_by(
                Expense.purchase_date.desc(),
                Expense.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        if start is not None:
            statement = statement.where(
                Expense.purchase_date >= start,
                Expense.purchase_date < end,
            )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def count_filtered(
        self,
        *,
        month: int | None = None,
        year: int | None = None,
    ) -> int:
        start, end = self._period_bounds(
            month,
            year,
        )

        statement = select(
            func.count(Expense.id)
        )

        if start is not None:
            statement = statement.where(
                Expense.purchase_date >= start,
                Expense.purchase_date < end,
            )

        return int(
            self.session.scalar(
                statement
            )
            or 0
        )

    def get_current_month(
        self,
        month: int,
        year: int,
    ) -> list[Expense]:
        start, end = self._period_bounds(
            month,
            year,
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

    def delete_by_id(
        self,
        expense_id: int,
    ) -> bool:
        expense = self.get_by_id(
            expense_id
        )

        if expense is None:
            return False

        self.delete(expense)

        return True
