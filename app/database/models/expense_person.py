from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ExpensePerson(Base):
    __tablename__ = "expense_people"

    id: Mapped[int] = mapped_column(primary_key=True)

    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id")
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id")
    )

    amount: Mapped[float] = mapped_column(Float)

    expense = relationship(
        "Expense",
        back_populates="people"
    )

    person = relationship(
        "Person",
        back_populates="expenses"
    )