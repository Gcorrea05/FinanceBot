import asyncio
from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from types import SimpleNamespace

from app.services.automation_service import (
    AutomationService,
)


class RepositoryStub:
    def __init__(self):
        self.settings = SimpleNamespace(
            enabled=True,
            telegram_chat_id="123",
            timezone="America/Sao_Paulo",
            daily_summary_enabled=True,
            daily_summary_hour=20,
            weekly_summary_enabled=False,
            weekly_summary_weekday=0,
            weekly_summary_hour=8,
            installment_reminders_enabled=True,
            installment_reminder_days=3,
            reminder_hour=9,
            budget_alerts_enabled=True,
            budget_alert_threshold=80,
        )
        self.deliveries = []

    def get_settings(self):
        return self.settings

    def list_expenses_between(
        self,
        **kwargs,
    ):
        del kwargs
        return []

    def pending_receivables_total(self):
        return Decimal("45.00")

    def list_unpaid_installments_until(
        self,
        **kwargs,
    ):
        del kwargs
        return []

    def delivery_exists(self, key):
        return any(
            item["deduplication_key"]
            == key
            for item in self.deliveries
        )

    def record_delivery(self, **values):
        self.deliveries.append(values)
        return SimpleNamespace(**values)

    def list_deliveries(self, limit=30):
        del limit
        return []

    def save_settings(self, **values):
        for name, value in values.items():
            setattr(self.settings, name, value)
        return self.settings

    def link_chat(self, chat_id):
        self.settings.telegram_chat_id = chat_id
        return self.settings

    def disconnect_chat(self):
        self.settings.telegram_chat_id = None
        return self.settings


class BudgetServiceStub:
    def get_overview(self, **kwargs):
        del kwargs
        return SimpleNamespace(
            configured=True,
            usage_percent=Decimal("85.00"),
            remaining=Decimal("450.00"),
        )


class SenderStub:
    def __init__(self):
        self.messages = []

    async def send(
        self,
        *,
        chat_id,
        message,
    ):
        self.messages.append(
            (chat_id, message)
        )


def test_builds_daily_and_budget_events():
    service = AutomationService(
        repository=RepositoryStub(),
        budget_service=BudgetServiceStub(),
    )

    events = service.preview(
        now=datetime(
            2026,
            7,
            24,
            20,
        )
    )

    assert {
        event.kind
        for event in events
    } == {
        "daily_summary",
        "budget_alert",
    }

    assert (
        "R$ 45,00"
        in events[0].message
    )


def test_run_due_is_idempotent():
    repository = RepositoryStub()
    sender = SenderStub()
    service = AutomationService(
        repository=repository,
        budget_service=BudgetServiceStub(),
    )
    now = datetime(
        2026,
        7,
        24,
        20,
    )

    first = asyncio.run(
        service.run_due(
            sender=sender,
            now=now,
        )
    )
    second = asyncio.run(
        service.run_due(
            sender=sender,
            now=now,
        )
    )

    assert first.sent == 2
    assert second.sent == 0
    assert second.skipped == 2
    assert len(sender.messages) == 2


def test_validates_timezone():
    service = AutomationService(
        repository=RepositoryStub(),
        budget_service=BudgetServiceStub(),
    )

    try:
        service.save_settings(
            enabled=True,
            timezone="Invalid/Timezone",
            daily_summary_enabled=True,
            daily_summary_hour=20,
            weekly_summary_enabled=True,
            weekly_summary_weekday=0,
            weekly_summary_hour=8,
            installment_reminders_enabled=True,
            installment_reminder_days=3,
            reminder_hour=9,
            budget_alerts_enabled=True,
            budget_alert_threshold=80,
        )
    except ValueError as error:
        assert (
            "Fuso horario invalido"
            in str(error)
        )
    else:
        raise AssertionError(
            "Timezone invalido foi aceito."
        )
