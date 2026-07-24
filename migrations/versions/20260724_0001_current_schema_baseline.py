"""Current FinanceBot schema baseline.

Revision ID: 20260724_0001
Revises:
Create Date: 2026-07-24
"""

from collections.abc import Sequence


revision: str = "20260724_0001"
down_revision: str | None = None
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
    # The schema existed before Alembic.
    # bootstrap_migrations creates or validates
    # it and then stamps this baseline.
    pass


def downgrade() -> None:
    # Baseline downgrade intentionally changes
    # no application tables.
    pass
