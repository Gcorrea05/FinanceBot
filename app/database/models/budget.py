from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "year",
            "month",
            name="uq_budget_period",
        ),
        CheckConstraint(
            "month >= 1 AND month <= 12",
            name="ck_budget_month",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    monthly_income: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
            asdecimal=True,
        ),
        nullable=False,
    )

    reserve_target: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
            asdecimal=True,
        ),
        nullable=False,
        default=Decimal("0.00"),
    )

    spending_limit: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
            asdecimal=True,
        ),
        nullable=False,
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
