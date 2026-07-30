from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.database.models import RecurringExpense, RecurringExpenseOccurrence


class RecurringExpenseRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_active(self) -> list[RecurringExpense]:
        return list(
            self.session.scalars(
                select(RecurringExpense)
                .options(
                    selectinload(RecurringExpense.category),
                    selectinload(RecurringExpense.payment_method),
                )
                .where(RecurringExpense.active.is_(True))
                .order_by(RecurringExpense.description)
            ).all()
        )

    def list_all(self) -> list[RecurringExpense]:
        return list(
            self.session.scalars(
                select(RecurringExpense)
                .options(
                    selectinload(RecurringExpense.category),
                    selectinload(RecurringExpense.payment_method),
                    selectinload(RecurringExpense.occurrences),
                )
                .order_by(RecurringExpense.description)
            ).unique().all()
        )

    def get_by_source_key(self, source_key: str) -> RecurringExpense | None:
        return self.session.scalar(
            select(RecurringExpense).where(RecurringExpense.source_key == source_key)
        )

    def get_occurrence(
        self, recurring_id: int, year: int, month: int
    ) -> RecurringExpenseOccurrence | None:
        return self.session.scalar(
            select(RecurringExpenseOccurrence).where(
                RecurringExpenseOccurrence.recurring_expense_id == recurring_id,
                RecurringExpenseOccurrence.competence_year == year,
                RecurringExpenseOccurrence.competence_month == month,
            )
        )

    def list_for_period(
        self, year: int, month: int
    ) -> list[RecurringExpenseOccurrence]:
        return list(
            self.session.scalars(
                select(RecurringExpenseOccurrence)
                .options(
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.category
                    ),
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.payment_method
                    ),
                )
                .where(
                    RecurringExpenseOccurrence.competence_year == year,
                    RecurringExpenseOccurrence.competence_month == month,
                )
                .order_by(RecurringExpenseOccurrence.due_date)
            ).all()
        )

    def list_planned_for_period(
        self, year: int, month: int
    ) -> list[RecurringExpenseOccurrence]:
        return list(
            self.session.scalars(
                select(RecurringExpenseOccurrence)
                .options(
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.category
                    ),
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.payment_method
                    ),
                )
                .where(
                    RecurringExpenseOccurrence.competence_year == year,
                    RecurringExpenseOccurrence.competence_month == month,
                    RecurringExpenseOccurrence.status == "planned",
                )
                .order_by(RecurringExpenseOccurrence.due_date)
            ).all()
        )

    def list_due(self, as_of: date) -> list[RecurringExpenseOccurrence]:
        return list(
            self.session.scalars(
                select(RecurringExpenseOccurrence)
                .join(RecurringExpense)
                .options(
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.category
                    ),
                    selectinload(RecurringExpenseOccurrence.recurring_expense).selectinload(
                        RecurringExpense.payment_method
                    ),
                )
                .where(
                    RecurringExpenseOccurrence.status == "planned",
                    RecurringExpenseOccurrence.due_date <= as_of,
                    RecurringExpense.active.is_(True),
                    RecurringExpense.auto_post.is_(True),
                )
                .order_by(RecurringExpenseOccurrence.due_date)
            ).all()
        )
