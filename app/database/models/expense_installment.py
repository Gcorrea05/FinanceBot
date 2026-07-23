from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ExpenseInstallment(Base):
    __tablename__ = "expense_installments"

    __table_args__ = (
        UniqueConstraint(
            "expense_id",
            "installment_number",
            name="uq_expense_installment_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    expense_id: Mapped[int] = mapped_column(
        ForeignKey(
            "expenses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    installment_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    total_installments: Mapped[int] = mapped_column(
        nullable=False,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    installment_value: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
            asdecimal=True,
        ),
        nullable=False,
    )

    is_paid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    expense = relationship(
        "Expense",
        back_populates="installments",
    )
