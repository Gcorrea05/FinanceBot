from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)

    purchase_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    purchase_place: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    purchase_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"),
        nullable=False,
        index=True,
    )

    is_installment: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_shared: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    category = relationship(
        "Category",
        back_populates="expenses",
    )

    payment_method = relationship(
        "PaymentMethod",
        back_populates="expenses",
    )

    installments: Mapped[list["ExpenseInstallment"]] = relationship(
        "ExpenseInstallment",
        back_populates="expense",
        cascade="all, delete-orphan",
        order_by="ExpenseInstallment.installment_number",
    )

    people: Mapped[list["ExpensePerson"]] = relationship(
        "ExpensePerson",
        back_populates="expense",
        cascade="all, delete-orphan",
    )
