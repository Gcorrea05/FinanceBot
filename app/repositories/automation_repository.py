from datetime import date, datetime

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.database.models import (
    AutomationDelivery,
    AutomationSettings,
    Expense,
    ExpenseInstallment,
    ExpensePerson,
)


class AutomationRepository:
    PROFILE_KEY = "default"

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get_settings(
        self,
    ) -> AutomationSettings | None:
        statement = select(
            AutomationSettings
        ).where(
            AutomationSettings.profile_key
            == self.PROFILE_KEY
        )

        return self.session.scalar(
            statement
        )

    def save_settings(
        self,
        **values,
    ) -> AutomationSettings:
        settings = self.get_settings()

        if settings is None:
            settings = AutomationSettings(
                profile_key=self.PROFILE_KEY,
                **values,
            )
            self.session.add(settings)
        else:
            for name, value in values.items():
                setattr(
                    settings,
                    name,
                    value,
                )

        self.session.commit()
        self.session.refresh(settings)

        return settings

    def link_chat(
        self,
        chat_id: str,
    ) -> AutomationSettings:
        settings = self.get_settings()

        if settings is None:
            settings = AutomationSettings(
                profile_key=self.PROFILE_KEY,
                telegram_chat_id=chat_id,
            )
            self.session.add(settings)
        else:
            settings.telegram_chat_id = chat_id

        self.session.commit()
        self.session.refresh(settings)

        return settings

    def disconnect_chat(
        self,
    ) -> AutomationSettings:
        settings = self.get_settings()

        if settings is None:
            settings = AutomationSettings(
                profile_key=self.PROFILE_KEY,
            )
            self.session.add(settings)
        else:
            settings.telegram_chat_id = None

        self.session.commit()
        self.session.refresh(settings)

        return settings

    def delivery_exists(
        self,
        deduplication_key: str,
    ) -> bool:
        statement = select(
            AutomationDelivery.id
        ).where(
            AutomationDelivery.deduplication_key
            == deduplication_key,
            AutomationDelivery.status
            == "sent",
        )

        return (
            self.session.scalar(statement)
            is not None
        )

    def record_delivery(
        self,
        *,
        kind: str,
        deduplication_key: str,
        status: str,
        message: str,
        scheduled_for: datetime | None,
        sent_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AutomationDelivery:
        delivery = AutomationDelivery(
            kind=kind,
            deduplication_key=(
                deduplication_key
            ),
            status=status,
            message=message,
            scheduled_for=scheduled_for,
            sent_at=sent_at,
            error_message=error_message,
        )

        self.session.add(delivery)
        self.session.commit()
        self.session.refresh(delivery)

        return delivery

    def list_deliveries(
        self,
        limit: int = 30,
    ) -> list[AutomationDelivery]:
        safe_limit = min(
            max(limit, 1),
            100,
        )

        statement = (
            select(AutomationDelivery)
            .order_by(
                AutomationDelivery
                .created_at
                .desc(),
                AutomationDelivery.id.desc(),
            )
            .limit(safe_limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    @staticmethod
    def _expense_options():
        return (
            selectinload(
                Expense.people
            ),
            selectinload(
                Expense.category
            ),
            selectinload(
                Expense.payment_method
            ),
            selectinload(
                Expense.installments
            ),
        )

    def list_expenses_between(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> list[Expense]:
        statement = (
            select(Expense)
            .options(
                *self._expense_options()
            )
            .where(
                Expense.purchase_date >= start,
                Expense.purchase_date < end,
            )
            .order_by(
                Expense.purchase_date.asc(),
                Expense.id.asc(),
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def list_unpaid_installments_until(
        self,
        *,
        end_date: date,
        limit: int = 50,
    ) -> list[ExpenseInstallment]:
        statement = (
            select(ExpenseInstallment)
            .join(Expense)
            .options(
                selectinload(
                    ExpenseInstallment.expense
                ).selectinload(
                    Expense.people
                ),
                selectinload(
                    ExpenseInstallment.expense
                ).selectinload(
                    Expense.category
                ),
            )
            .where(
                ExpenseInstallment.is_paid
                .is_(False),
                ExpenseInstallment.due_date
                <= end_date,
            )
            .order_by(
                ExpenseInstallment
                .due_date
                .asc(),
                ExpenseInstallment.id.asc(),
            )
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def pending_receivables_total(
        self,
    ):
        statement = select(
            func.coalesce(
                func.sum(
                    ExpensePerson.shared_value
                ),
                0,
            )
        ).where(
            ExpensePerson.is_settled.is_(False)
        )

        return self.session.scalar(
            statement
        )
