from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class AutomationSettingsRequest(
    BaseModel
):
    enabled: bool
    timezone: str = Field(
        min_length=1,
        max_length=80,
    )
    daily_summary_enabled: bool
    daily_summary_hour: int = Field(
        ge=0,
        le=23,
    )
    weekly_summary_enabled: bool
    weekly_summary_weekday: int = Field(
        ge=0,
        le=6,
    )
    weekly_summary_hour: int = Field(
        ge=0,
        le=23,
    )
    installment_reminders_enabled: bool
    installment_reminder_days: int = Field(
        ge=0,
        le=30,
    )
    reminder_hour: int = Field(
        ge=0,
        le=23,
    )
    budget_alerts_enabled: bool
    budget_alert_threshold: int = Field(
        ge=1,
        le=100,
    )


class AutomationSettingsResponse(
    AutomationSettingsRequest
):
    telegram_connected: bool


class AutomationMessageResponse(
    BaseModel
):
    kind: str
    title: str
    message: str
    scheduled_for: datetime | None


class AutomationPreviewResponse(
    BaseModel
):
    items: list[
        AutomationMessageResponse
    ]


class AutomationRunResponse(
    BaseModel
):
    generated: int
    sent: int
    skipped: int
    failed: int
    items: list[
        AutomationMessageResponse
    ]


class AutomationDeliveryResponse(
    BaseModel
):
    id: int
    kind: str
    status: str
    message: str
    scheduled_for: datetime | None
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime


class AutomationHistoryResponse(
    BaseModel
):
    items: list[
        AutomationDeliveryResponse
    ]
