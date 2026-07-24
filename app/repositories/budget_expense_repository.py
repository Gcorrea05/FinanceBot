from datetime import date, datetime

from sqlalchemy import (
    and_,
    or_,
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.database.models import (
    Expense,
    ExpenseInstallment,
    ExpensePerson,
)


class BudgetExpenseRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    @staticmethod
    def _bounds(
        *,
        year: int,
        month: int,
    ) -> tuple[
        datetime,
        datetime,
        date,
        date,
    ]:
        start_datetime = datetime(
            year,
            month,
            1,
        )

        start_date = date(
            year,
            month,
            1,
        )

        if month == 12:
            end_datetime = datetime(
                year + 1,
                1,
                1,
            )
            end_date = date(
                year + 1,
                1,
                1,
            )
        else:
            end_datetime = datetime(
                year,
                month + 1,
                1,
            )
            end_date = date(
                year,
                month + 1,
                1,
            )

        return (
            start_datetime,
            end_datetime,
            start_date,
            end_date,
        )

    def list_for_period(
        self,
        *,
        year: int,
        month: int,
    ) -> list[Expense]:
        (
            start_datetime,
            end_datetime,
            start_date,
            end_date,
        ) = self._bounds(
            year=year,
            month=month,
        )

        statement = (
            select(Expense)
            .options(
                selectinload(
                    Expense.installments
                ),
                selectinload(
                    Expense.people
                ).selectinload(
                    ExpensePerson.person
                ),
            )
            .where(
                or_(
                    and_(
                        Expense.is_installment.is_(False),
                        Expense.purchase_date >= start_datetime,
                        Expense.purchase_date < end_datetime,
                    ),
                    and_(
                        Expense.is_installment.is_(True),
                        Expense.installments.any(
                            and_(
                                ExpenseInstallment.due_date >= start_date,
                                ExpenseInstallment.due_date < end_date,
                            )
                        ),
                    ),
                )
            )
        )

        return list(
            self.session.scalars(
                statement
            ).unique().all()
        )
