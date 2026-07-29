from datetime import datetime

from app.events.model import DomainEvent
from app.events.publisher import EventPublisher


def _period_from_expense(expense) -> tuple[int | None, int | None]:
    purchase_date = getattr(expense, "purchase_date", None)
    if isinstance(purchase_date, datetime):
        return purchase_date.year, purchase_date.month
    return None, None


class _Proxy:
    def __init__(self, service, publisher: EventPublisher):
        self._service = service
        self._publisher = publisher

    def __getattr__(self, name: str):
        return getattr(self._service, name)

    def _publish(
        self,
        *,
        name: str,
        aggregate_type: str,
        aggregate_id,
        payload: dict | None = None,
    ) -> None:
        self._publisher.publish(
            DomainEvent.new(
                name=name,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                payload=payload,
            )
        )


class EventAwareExpenseService(_Proxy):
    def create_expense(self, data):
        expense = self._service.create_expense(data)
        year, month = _period_from_expense(expense)
        self._publish(
            name="expense.created",
            aggregate_type="expense",
            aggregate_id=expense.id,
            payload={
                "year": year,
                "month": month,
                "purchase_value": str(expense.purchase_value),
            },
        )
        return expense


class EventAwareExpenseEditorService(_Proxy):
    def update(self, expense_id: int, data):
        expense = self._service.update(expense_id, data)
        year, month = _period_from_expense(expense)
        self._publish(
            name="expense.updated",
            aggregate_type="expense",
            aggregate_id=expense.id,
            payload={"year": year, "month": month},
        )
        return expense


class EventAwareExpenseManagementService(_Proxy):
    def delete(self, expense_id: int) -> None:
        expense = self._service.get(expense_id)
        year, month = _period_from_expense(expense)
        self._service.delete(expense_id)
        self._publish(
            name="expense.deleted",
            aggregate_type="expense",
            aggregate_id=expense_id,
            payload={"year": year, "month": month},
        )


class EventAwareBudgetService(_Proxy):
    def save_plan(self, **kwargs):
        overview = self._service.save_plan(**kwargs)
        self._publish(
            name="budget.updated",
            aggregate_type="budget",
            aggregate_id=f"{overview.year}-{overview.month:02d}",
            payload={"year": overview.year, "month": overview.month},
        )
        return overview


class EventAwareReceivableService(_Proxy):
    def settle(self, receivable_id: int):
        receivable = self._service.settle(receivable_id)
        year, month = _period_from_expense(
            getattr(receivable, "expense", None)
        )
        self._publish(
            name="receivable.settled",
            aggregate_type="receivable",
            aggregate_id=receivable_id,
            payload={"year": year, "month": month},
        )
        return receivable

    def reopen(self, receivable_id: int):
        receivable = self._service.reopen(receivable_id)
        year, month = _period_from_expense(
            getattr(receivable, "expense", None)
        )
        self._publish(
            name="receivable.reopened",
            aggregate_type="receivable",
            aggregate_id=receivable_id,
            payload={"year": year, "month": month},
        )
        return receivable


class EventAwareImportService(_Proxy):
    def confirm(self, batch_id: int):
        batch = self._service.confirm(batch_id)
        self._publish(
            name="import.completed",
            aggregate_type="import",
            aggregate_id=batch.id,
            payload={"imported_rows": batch.imported_rows},
        )
        return batch
