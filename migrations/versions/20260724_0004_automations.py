"""Add automation settings and delivery history.

Revision ID: 20260724_0004
Revises: 20260724_0003
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260724_0004"
down_revision: str | None = "20260724_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "automation_settings",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "profile_key",
            sa.String(length=40),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "telegram_chat_id",
            sa.String(length=64),
            nullable=True,
        ),
        sa.Column(
            "timezone",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "daily_summary_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "daily_summary_hour",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "weekly_summary_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "weekly_summary_weekday",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "weekly_summary_hour",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "installment_reminders_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "installment_reminder_days",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "reminder_hour",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "budget_alerts_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "budget_alert_threshold",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.CheckConstraint(
            (
                "daily_summary_hour >= 0 "
                "AND daily_summary_hour <= 23"
            ),
            name="ck_automation_daily_hour",
        ),
        sa.CheckConstraint(
            (
                "weekly_summary_hour >= 0 "
                "AND weekly_summary_hour <= 23"
            ),
            name="ck_automation_weekly_hour",
        ),
        sa.CheckConstraint(
            (
                "weekly_summary_weekday >= 0 "
                "AND weekly_summary_weekday <= 6"
            ),
            name="ck_automation_weekday",
        ),
        sa.CheckConstraint(
            (
                "reminder_hour >= 0 "
                "AND reminder_hour <= 23"
            ),
            name="ck_automation_reminder_hour",
        ),
        sa.CheckConstraint(
            (
                "installment_reminder_days >= 0 "
                "AND installment_reminder_days <= 30"
            ),
            name="ck_automation_reminder_days",
        ),
        sa.CheckConstraint(
            (
                "budget_alert_threshold >= 1 "
                "AND budget_alert_threshold <= 100"
            ),
            name="ck_automation_budget_threshold",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "profile_key",
            name=(
                "uq_automation_settings_"
                "profile"
            ),
        ),
    )

    op.create_table(
        "automation_deliveries",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "kind",
            sa.String(length=40),
            nullable=False,
        ),
        sa.Column(
            "deduplication_key",
            sa.String(length=180),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "scheduled_for",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "deduplication_key",
            name=(
                "uq_automation_"
                "delivery_key"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_automation_deliveries_"
            "created_at"
        ),
        "automation_deliveries",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f(
            "ix_automation_deliveries_kind"
        ),
        "automation_deliveries",
        ["kind"],
        unique=False,
    )
    op.create_index(
        op.f(
            "ix_automation_deliveries_status"
        ),
        "automation_deliveries",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_automation_deliveries_status"
        ),
        table_name="automation_deliveries",
    )
    op.drop_index(
        op.f(
            "ix_automation_deliveries_kind"
        ),
        table_name="automation_deliveries",
    )
    op.drop_index(
        op.f(
            "ix_automation_deliveries_"
            "created_at"
        ),
        table_name="automation_deliveries",
    )
    op.drop_table(
        "automation_deliveries"
    )
    op.drop_table(
        "automation_settings"
    )
