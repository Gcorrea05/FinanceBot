from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"

    __table_args__ = (
        CheckConstraint("due_day >= 1 AND due_day <= 31", name="ck_recurring_due_day"),
        CheckConstraint("amount > 0", name="ck_recurring_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2, asdecimal=True), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"), nullable=False, index=True
    )
    due_day: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_post: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_key: Mapped[str | None] = mapped_column(
        String(120), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    category = relationship("Category")
    payment_method = relationship("PaymentMethod")
    occurrences: Mapped[list["RecurringExpenseOccurrence"]] = relationship(
        "RecurringExpenseOccurrence",
        back_populates="recurring_expense",
        cascade="all, delete-orphan",
        order_by="RecurringExpenseOccurrence.due_date",
    )


class RecurringExpenseOccurrence(Base):
    __tablename__ = "recurring_expense_occurrences"

    __table_args__ = (
        UniqueConstraint(
            "recurring_expense_id",
            "competence_year",
            "competence_month",
            name="uq_recurring_occurrence_competence",
        ),
        CheckConstraint(
            "competence_month >= 1 AND competence_month <= 12",
            name="ck_recurring_occurrence_month",
        ),
        CheckConstraint("amount > 0", name="ck_recurring_occurrence_amount_positive"),
        CheckConstraint(
            "status IN ('planned', 'posted', 'skipped', 'cancelled')",
            name="ck_recurring_occurrence_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recurring_expense_id: Mapped[int] = mapped_column(
        ForeignKey("recurring_expenses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competence_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    competence_month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2, asdecimal=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="planned", index=True
    )
    expense_id: Mapped[int | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    recurring_expense: Mapped[RecurringExpense] = relationship(
        "RecurringExpense", back_populates="occurrences"
    )
    expense = relationship("Expense")
