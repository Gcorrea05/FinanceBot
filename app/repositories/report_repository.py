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


class ReportRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    @staticmethod
    def _bounds(
        *,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ) -> tuple[
        datetime,
        datetime,
        date,
        date,
    ]:
        start_datetime = datetime(
            start_year,
            start_month,
            1,
        )
        start_date = date(
            start_year,
            start_month,
            1,
        )

        if end_month == 12:
            end_datetime = datetime(
                end_year + 1,
                1,
                1,
            )
            end_date = date(
                end_year + 1,
                1,
                1,
            )
        else:
            end_datetime = datetime(
                end_year,
                end_month + 1,
                1,
            )
            end_date = date(
                end_year,
                end_month + 1,
                1,
            )

        return (
            start_datetime,
            end_datetime,
            start_date,
            end_date,
        )

    @staticmethod
    def _detail_options():
        return (
            selectinload(Expense.category),
            selectinload(Expense.payment_method),
            selectinload(Expense.installments),
            selectinload(Expense.people).selectinload(
                ExpensePerson.person
            ),
        )

    def list_for_period(
        self,
        *,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        category: str | None = None,
        payment_method: str | None = None,
        place: str | None = None,
    ) -> list[Expense]:
        (
            start_datetime,
            end_datetime,
            start_date,
            end_date,
        ) = self._bounds(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        statement = (
            select(Expense)
            .options(*self._detail_options())
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
            .order_by(
                Expense.purchase_date.asc(),
                Expense.id.asc(),
            )
        )

        if category:
            statement = statement.where(
                Expense.category.has(name=category)
            )

        if payment_method:
            statement = statement.where(
                Expense.payment_method.has(name=payment_method)
            )

        if place:
            statement = statement.where(
                Expense.purchase_place.ilike(
                    f"%{place.strip()}%"
                )
            )

        return list(
            self.session.scalars(statement).unique().all()
        )

    def list_purchases_for_month(
        self,
        *,
        year: int,
        month: int,
    ) -> list[Expense]:
        (
            start_datetime,
            end_datetime,
            _,
            _,
        ) = self._bounds(
            start_year=year,
            start_month=month,
            end_year=year,
            end_month=month,
        )

        statement = (
            select(Expense)
            .options(*self._detail_options())
            .where(
                Expense.purchase_date >= start_datetime,
                Expense.purchase_date < end_datetime,
            )
            .order_by(
                Expense.purchase_date.asc(),
                Expense.id.asc(),
            )
        )

        return list(
            self.session.scalars(statement).unique().all()
        )
