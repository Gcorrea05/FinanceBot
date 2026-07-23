from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ExpenseInstallment(Base):
    __tablename__ = "expense_installments"

    id: Mapped[int] = mapped_column(primary_key=True)

    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id")
    )

    installment_number: Mapped[int]

    installment_value: Mapped[float] = mapped_column(Float)

    due_date: Mapped[date]

    paid: Mapped[bool] = mapped_column(Boolean, default=False)

    expense = relationship(
        "Expense",
        back_populates="installments"
    )