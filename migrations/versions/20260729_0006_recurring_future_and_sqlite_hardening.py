"""Recurring expenses, future planning and SQLite money hardening.

Revision ID: 20260729_0006
Revises: 20260724_0005
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260729_0006"
down_revision: str | None = "20260724_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _indexes(table_name: str) -> set[str]:
    return {
        item["name"]
        for item in sa.inspect(op.get_bind()).get_indexes(table_name)
        if item.get("name")
    }


def upgrade() -> None:
    tables = _tables()

    if "expenses" in tables:
        columns = {
            item["name"]: item
            for item in sa.inspect(op.get_bind()).get_columns("expenses")
        }
        purchase = columns.get("purchase_value")
        if purchase is not None and not isinstance(purchase["type"], sa.Numeric):
            with op.batch_alter_table("expenses", recreate="always") as batch:
                batch.alter_column(
                    "purchase_value",
                    existing_type=purchase["type"],
                    type_=sa.Numeric(precision=12, scale=2, asdecimal=True),
                    existing_nullable=False,
                )

    tables = _tables()
    if "financial_profiles" not in tables:
        op.create_table(
            "financial_profiles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("profile_key", sa.String(length=40), nullable=False),
            sa.Column(
                "credit_card_cycle_start_day",
                sa.Integer(),
                nullable=False,
                server_default="27",
            ),
            sa.Column(
                "credit_card_closing_day",
                sa.Integer(),
                nullable=False,
                server_default="26",
            ),
            sa.Column(
                "credit_card_installment_day",
                sa.Integer(),
                nullable=False,
                server_default="26",
            ),
            sa.Column(
                "projection_months",
                sa.Integer(),
                nullable=False,
                server_default="12",
            ),
            sa.Column(
                "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.Column(
                "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.UniqueConstraint("profile_key", name="uq_financial_profile_key"),
            sa.CheckConstraint(
                "credit_card_cycle_start_day >= 1 AND credit_card_cycle_start_day <= 31",
                name="ck_financial_profile_cycle_start_day",
            ),
            sa.CheckConstraint(
                "credit_card_closing_day >= 1 AND credit_card_closing_day <= 31",
                name="ck_financial_profile_closing_day",
            ),
            sa.CheckConstraint(
                "credit_card_installment_day >= 1 AND credit_card_installment_day <= 31",
                name="ck_financial_profile_installment_day",
            ),
            sa.CheckConstraint(
                "projection_months >= 1 AND projection_months <= 60",
                name="ck_financial_profile_projection_months",
            ),
        )

    tables = _tables()
    if "recurring_expenses" not in tables:
        op.create_table(
            "recurring_expenses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("description", sa.String(length=255), nullable=False),
            sa.Column(
                "amount", sa.Numeric(precision=12, scale=2, asdecimal=True), nullable=False
            ),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("payment_method_id", sa.Integer(), nullable=False),
            sa.Column("due_day", sa.Integer(), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("auto_post", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("source_key", sa.String(length=120), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.Column(
                "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
            sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"]),
            sa.UniqueConstraint("source_key", name="uq_recurring_expense_source_key"),
            sa.CheckConstraint("due_day >= 1 AND due_day <= 31", name="ck_recurring_due_day"),
            sa.CheckConstraint("amount > 0", name="ck_recurring_amount_positive"),
        )
        op.create_index(
            "ix_recurring_expenses_category_id", "recurring_expenses", ["category_id"]
        )
        op.create_index(
            "ix_recurring_expenses_payment_method_id",
            "recurring_expenses",
            ["payment_method_id"],
        )

    tables = _tables()
    if "recurring_expense_occurrences" not in tables:
        op.create_table(
            "recurring_expense_occurrences",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("recurring_expense_id", sa.Integer(), nullable=False),
            sa.Column("competence_year", sa.Integer(), nullable=False),
            sa.Column("competence_month", sa.Integer(), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=False),
            sa.Column(
                "amount", sa.Numeric(precision=12, scale=2, asdecimal=True), nullable=False
            ),
            sa.Column(
                "status", sa.String(length=20), nullable=False, server_default="planned"
            ),
            sa.Column("expense_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.Column("posted_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(
                ["recurring_expense_id"],
                ["recurring_expenses.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="SET NULL"),
            sa.UniqueConstraint(
                "recurring_expense_id",
                "competence_year",
                "competence_month",
                name="uq_recurring_occurrence_competence",
            ),
            sa.UniqueConstraint("expense_id", name="uq_recurring_occurrence_expense"),
            sa.CheckConstraint(
                "competence_month >= 1 AND competence_month <= 12",
                name="ck_recurring_occurrence_month",
            ),
            sa.CheckConstraint("amount > 0", name="ck_recurring_occurrence_amount_positive"),
            sa.CheckConstraint(
                "status IN ('planned', 'posted', 'skipped', 'cancelled')",
                name="ck_recurring_occurrence_status",
            ),
        )
        op.create_index(
            "ix_recurring_occurrence_period",
            "recurring_expense_occurrences",
            ["competence_year", "competence_month", "status"],
        )
        op.create_index(
            "ix_recurring_occurrence_due",
            "recurring_expense_occurrences",
            ["due_date", "status"],
        )

    bind = op.get_bind()
    rows = bind.execute(
        sa.text("SELECT id, name FROM payment_methods ORDER BY id")
    ).mappings().all()
    groups = {
        "Cartão de crédito": {
            "credito", "crédito", "cartao de credito", "cartão de crédito"
        },
        "Débito": {
            "debito", "débito", "cartao de debito", "cartão de débito"
        },
    }
    for target, aliases in groups.items():
        matches = [row for row in rows if row["name"].strip().lower() in aliases]
        if not matches:
            continue
        canonical = next((row for row in matches if row["name"] == target), matches[0])
        bind.execute(
            sa.text("UPDATE payment_methods SET name=:name WHERE id=:id"),
            {"name": target, "id": canonical["id"]},
        )
        for duplicate in matches:
            if duplicate["id"] == canonical["id"]:
                continue
            bind.execute(
                sa.text(
                    "UPDATE expenses SET payment_method_id=:target "
                    "WHERE payment_method_id=:duplicate"
                ),
                {"target": canonical["id"], "duplicate": duplicate["id"]},
            )
            bind.execute(
                sa.text("DELETE FROM payment_methods WHERE id=:id"),
                {"id": duplicate["id"]},
            )

    op.execute(
        """
        INSERT INTO financial_profiles (
            profile_key,
            credit_card_cycle_start_day,
            credit_card_closing_day,
            credit_card_installment_day,
            projection_months
        )
        SELECT 'default', 27, 26, 26, 12
        WHERE NOT EXISTS (
            SELECT 1 FROM financial_profiles WHERE profile_key = 'default'
        )
        """
    )


def downgrade() -> None:
    tables = _tables()
    if "recurring_expense_occurrences" in tables:
        op.drop_table("recurring_expense_occurrences")
    tables = _tables()
    if "recurring_expenses" in tables:
        op.drop_table("recurring_expenses")
    tables = _tables()
    if "financial_profiles" in tables:
        op.drop_table("financial_profiles")
    if "expenses" in _tables():
        with op.batch_alter_table("expenses", recreate="always") as batch:
            batch.alter_column(
                "purchase_value",
                existing_type=sa.Numeric(precision=12, scale=2, asdecimal=True),
                type_=sa.Float(),
                existing_nullable=False,
            )
