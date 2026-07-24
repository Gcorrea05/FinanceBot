"""Add monthly budget planning.

Revision ID: 20260724_0002
Revises: 20260724_0001
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260724_0002"
down_revision: str | None = "20260724_0001"
branch_labels: (
    str
    | Sequence[str]
    | None
) = None
depends_on: (
    str
    | Sequence[str]
    | None
) = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "year",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "month",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "monthly_income",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=False,
        ),
        sa.Column(
            "reserve_target",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=False,
        ),
        sa.Column(
            "spending_limit",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
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
            "month >= 1 AND month <= 12",
            name="ck_budget_month",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "year",
            "month",
            name="uq_budget_period",
        ),
    )

    op.create_index(
        op.f("ix_budgets_year"),
        "budgets",
        ["year"],
        unique=False,
    )

    op.create_index(
        op.f("ix_budgets_month"),
        "budgets",
        ["month"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_budgets_month"),
        table_name="budgets",
    )

    op.drop_index(
        op.f("ix_budgets_year"),
        table_name="budgets",
    )

    op.drop_table("budgets")
