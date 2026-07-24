"""Add import preview and history.

Revision ID: 20260724_0003
Revises: 20260724_0002
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260724_0003"
down_revision: str | None = "20260724_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("default_category", sa.String(length=100), nullable=False),
        sa.Column("default_payment_method", sa.String(length=100), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("ready_rows", sa.Integer(), nullable=False),
        sa.Column("duplicate_rows", sa.Integer(), nullable=False),
        sa.Column("invalid_rows", sa.Integer(), nullable=False),
        sa.Column("imported_rows", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_import_batches_status"), "import_batches", ["status"], unique=False)

    op.create_table(
        "import_rows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("purchase_place", sa.String(length=255), nullable=True),
        sa.Column("purchase_value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("fingerprint", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("expense_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["import_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id", "row_number", name="uq_import_row_number"),
    )
    op.create_index(op.f("ix_import_rows_batch_id"), "import_rows", ["batch_id"], unique=False)
    op.create_index(op.f("ix_import_rows_expense_id"), "import_rows", ["expense_id"], unique=False)
    op.create_index(op.f("ix_import_rows_fingerprint"), "import_rows", ["fingerprint"], unique=False)
    op.create_index(op.f("ix_import_rows_status"), "import_rows", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_import_rows_status"), table_name="import_rows")
    op.drop_index(op.f("ix_import_rows_fingerprint"), table_name="import_rows")
    op.drop_index(op.f("ix_import_rows_expense_id"), table_name="import_rows")
    op.drop_index(op.f("ix_import_rows_batch_id"), table_name="import_rows")
    op.drop_table("import_rows")
    op.drop_index(op.f("ix_import_batches_status"), table_name="import_batches")
    op.drop_table("import_batches")
