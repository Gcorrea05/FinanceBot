from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AutomationSettings(Base):
    __tablename__ = "automation_settings"

    __table_args__ = (
        UniqueConstraint(
            "profile_key",
            name="uq_automation_settings_profile",
        ),
        CheckConstraint(
            "daily_summary_hour >= 0 AND daily_summary_hour <= 23",
            name="ck_automation_daily_hour",
        ),
        CheckConstraint(
            "weekly_summary_hour >= 0 AND weekly_summary_hour <= 23",
            name="ck_automation_weekly_hour",
        ),
        CheckConstraint(
            (
                "weekly_summary_weekday >= 0 "
                "AND weekly_summary_weekday <= 6"
            ),
            name="ck_automation_weekday",
        ),
        CheckConstraint(
            "reminder_hour >= 0 AND reminder_hour <= 23",
            name="ck_automation_reminder_hour",
        ),
        CheckConstraint(
            (
                "installment_reminder_days >= 0 "
                "AND installment_reminder_days <= 30"
            ),
            name="ck_automation_reminder_days",
        ),
        CheckConstraint(
            (
                "budget_alert_threshold >= 1 "
                "AND budget_alert_threshold <= 100"
            ),
            name="ck_automation_budget_threshold",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    profile_key: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="default",
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="America/Sao_Paulo",
    )

    daily_summary_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    daily_summary_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
    )

    weekly_summary_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    weekly_summary_weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    weekly_summary_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8,
    )

    installment_reminders_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    installment_reminder_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    reminder_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=9,
    )

    budget_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    budget_alert_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=80,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class AutomationDelivery(Base):
    __tablename__ = "automation_deliveries"

    __table_args__ = (
        UniqueConstraint(
            "deduplication_key",
            name="uq_automation_delivery_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    kind: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    deduplication_key: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    scheduled_for: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
