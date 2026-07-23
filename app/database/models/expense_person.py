from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ExpensePerson(Base):
    __tablename__ = "expense_people"

    __table_args__ = (
        UniqueConstraint(
            "expense_id",
            "person_id",
            name="uq_expense_person",
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

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
        index=True,
    )

    shared_value: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
            asdecimal=True,
        ),
        nullable=False,
    )

    is_settled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    settled_at: Mapped[datetime | None] = mapped_column(
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
        back_populates="people",
    )

    person = relationship(
        "Person",
        back_populates="expenses",
    )
