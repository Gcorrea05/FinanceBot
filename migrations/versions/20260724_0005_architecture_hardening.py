"""Architecture hardening and event journal.

Revision ID: 20260724_0005
Revises: 20260724_0004
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260724_0005"
down_revision: str | None = "20260724_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        item["name"]
        for item in inspector.get_indexes(table_name)
        if item.get("name")
    }


def _create_index(name: str, table_name: str, columns: list[str]) -> None:
    if name in _index_names(table_name):
        return
    op.create_index(name, table_name, columns, unique=False)


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "domain_events" not in tables:
        op.create_table(
            "domain_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("event_id", sa.String(length=40), nullable=False),
            sa.Column("event_name", sa.String(length=100), nullable=False),
            sa.Column("aggregate_type", sa.String(length=60), nullable=False),
            sa.Column("aggregate_id", sa.String(length=80), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            ),
            sa.Column(
                "attempts",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "available_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("occurred_at", sa.DateTime(), nullable=False),
            sa.Column("processed_at", sa.DateTime(), nullable=True),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.UniqueConstraint("event_id", name="uq_domain_event_id"),
        )

    _create_index(
        "ix_domain_events_status_available",
        "domain_events",
        ["status", "available_at"],
    )
    _create_index(
        "ix_domain_events_aggregate",
        "domain_events",
        ["aggregate_type", "aggregate_id"],
    )
    _create_index(
        "ix_expenses_date_category",
        "expenses",
        ["purchase_date", "category_id"],
    )
    _create_index(
        "ix_expenses_date_payment",
        "expenses",
        ["purchase_date", "payment_method_id"],
    )
    _create_index(
        "ix_expense_people_open_person",
        "expense_people",
        ["is_settled", "person_id"],
    )
    _create_index(
        "ix_installments_due_paid",
        "expense_installments",
        ["due_date", "is_paid"],
    )
    _create_index(
        "ix_import_rows_status_fingerprint",
        "import_rows",
        ["status", "fingerprint"],
    )

    op.execute("DROP VIEW IF EXISTS vw_open_receivables")
    op.execute(
        """
        CREATE VIEW vw_open_receivables AS
        SELECT
            ep.id AS receivable_id,
            ep.expense_id,
            ep.person_id,
            p.name AS person_name,
            e.purchase_date,
            e.purchase_place,
            ep.shared_value
        FROM expense_people ep
        JOIN people p ON p.id = ep.person_id
        JOIN expenses e ON e.id = ep.expense_id
        WHERE ep.is_settled = 0
        """
    )

    op.execute("DROP VIEW IF EXISTS vw_installments_due")
    op.execute(
        """
        CREATE VIEW vw_installments_due AS
        SELECT
            i.id AS installment_id,
            i.expense_id,
            i.installment_number,
            i.total_installments,
            i.due_date,
            i.installment_value,
            i.is_paid,
            e.purchase_place,
            e.category_id,
            e.payment_method_id
        FROM expense_installments i
        JOIN expenses e ON e.id = i.expense_id
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS vw_installments_due")
    op.execute("DROP VIEW IF EXISTS vw_open_receivables")

    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    specs = (
        ("import_rows", "ix_import_rows_status_fingerprint"),
        ("expense_installments", "ix_installments_due_paid"),
        ("expense_people", "ix_expense_people_open_person"),
        ("expenses", "ix_expenses_date_payment"),
        ("expenses", "ix_expenses_date_category"),
        ("domain_events", "ix_domain_events_aggregate"),
        ("domain_events", "ix_domain_events_status_available"),
    )

    for table_name, index_name in specs:
        if table_name not in tables:
            continue
        names = {
            item["name"]
            for item in inspector.get_indexes(table_name)
            if item.get("name")
        }
        if index_name in names:
            op.drop_index(index_name, table_name=table_name)

    if "domain_events" in tables:
        op.drop_table("domain_events")
