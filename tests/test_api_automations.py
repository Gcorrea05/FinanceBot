from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import (
    get_container,
)
from app.services.automation_service import (
    AutomationEvent,
    AutomationRunResult,
    AutomationSettingsView,
)


class AutomationServiceStub:
    def __init__(self):
        self.saved = None

    def get_settings(self):
        return self._settings()

    def save_settings(self, **values):
        self.saved = values
        return self._settings()

    def disconnect_telegram(self):
        return self._settings(
            connected=False
        )

    def preview(self):
        return [
            AutomationEvent(
                kind="daily_summary",
                title="Resumo diario",
                message="Teste",
                deduplication_key="daily:test",
                scheduled_for=None,
            )
        ]

    async def run_due(self, **kwargs):
        del kwargs
        event = self.preview()[0]
        return AutomationRunResult(
            generated=1,
            sent=1,
            skipped=0,
            failed=0,
            events=[event],
        )

    def list_deliveries(self, limit=30):
        del limit
        return [
            SimpleNamespace(
                id=1,
                kind="daily_summary",
                status="sent",
                message="Teste",
                scheduled_for=None,
                sent_at=datetime(
                    2026,
                    7,
                    24,
                    20,
                ),
                error_message=None,
                created_at=datetime(
                    2026,
                    7,
                    24,
                    20,
                ),
            )
        ]

    @staticmethod
    def _settings(
        connected=True,
    ):
        return AutomationSettingsView(
            enabled=True,
            telegram_connected=connected,
            timezone="America/Sao_Paulo",
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


def make_client():
    application = create_app()
    service = AutomationServiceStub()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        automation_service=service
    )

    return (
        TestClient(application),
        service,
    )


def test_get_and_save_settings():
    client, service = make_client()

    response = client.get(
        "/api/v1/automations/settings"
    )

    assert response.status_code == 200
    assert (
        response.json()[
            "telegram_connected"
        ]
        is True
    )

    payload = {
        "enabled": True,
        "timezone": "America/Sao_Paulo",
        "daily_summary_enabled": True,
        "daily_summary_hour": 21,
        "weekly_summary_enabled": True,
        "weekly_summary_weekday": 4,
        "weekly_summary_hour": 8,
        "installment_reminders_enabled": True,
        "installment_reminder_days": 5,
        "reminder_hour": 9,
        "budget_alerts_enabled": True,
        "budget_alert_threshold": 75,
    }

    response = client.put(
        "/api/v1/automations/settings",
        json=payload,
    )

    assert response.status_code == 200
    assert (
        service.saved[
            "daily_summary_hour"
        ]
        == 21
    )


def test_preview_and_history():
    client, _ = make_client()

    preview = client.get(
        "/api/v1/automations/preview"
    )

    history = client.get(
        "/api/v1/automations/deliveries"
    )

    assert preview.status_code == 200
    assert (
        preview.json()["items"][0]["kind"]
        == "daily_summary"
    )
    assert history.status_code == 200
    assert (
        history.json()["items"][0]["status"]
        == "sent"
    )
