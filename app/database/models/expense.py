from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)

    purchase_date: Mapped[datetime]

    purchase_place: Mapped[str] = mapped_column(String(255))

    purchase_value: Mapped[float] = mapped_column(Float)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id")
    )

    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id")
    )

    is_installment: Mapped[bool] = mapped_column(Boolean, default=False)

    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    category = relationship("Category", back_populates="expenses")

    payment_method = relationship(
        "PaymentMethod",
        back_populates="expenses"
    )

    installments = relationship(
        "ExpenseInstallment",
        back_populates="expense",
        cascade="all, delete-orphan"
    )

    people = relationship(
        "ExpensePerson",
        back_populates="expense",
        cascade="all, delete-orphan"
    )