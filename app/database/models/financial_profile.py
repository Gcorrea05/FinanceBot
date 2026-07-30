from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    __table_args__ = (
        UniqueConstraint("profile_key", name="uq_financial_profile_key"),
        CheckConstraint(
            "credit_card_cycle_start_day >= 1 AND credit_card_cycle_start_day <= 31",
            name="ck_financial_profile_cycle_start_day",
        ),
        CheckConstraint(
            "credit_card_closing_day >= 1 AND credit_card_closing_day <= 31",
            name="ck_financial_profile_closing_day",
        ),
        CheckConstraint(
            "credit_card_installment_day >= 1 AND credit_card_installment_day <= 31",
            name="ck_financial_profile_installment_day",
        ),
        CheckConstraint(
            "projection_months >= 1 AND projection_months <= 60",
            name="ck_financial_profile_projection_months",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_key: Mapped[str] = mapped_column(
        String(40), nullable=False, default="default"
    )
    credit_card_cycle_start_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=27
    )
    credit_card_closing_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=26
    )
    credit_card_installment_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=26
    )
    projection_months: Mapped[int] = mapped_column(
        Integer, nullable=False, default=12
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
