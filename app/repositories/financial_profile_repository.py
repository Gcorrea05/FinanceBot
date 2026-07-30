from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import FinancialProfile


class FinancialProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_default(self) -> FinancialProfile | None:
        return self.session.scalar(
            select(FinancialProfile).where(FinancialProfile.profile_key == "default")
        )

    def get_or_create_default(self) -> FinancialProfile:
        profile = self.get_default()
        if profile is None:
            profile = FinancialProfile(
                profile_key="default",
                credit_card_cycle_start_day=27,
                credit_card_closing_day=26,
                credit_card_installment_day=26,
                projection_months=12,
            )
            self.session.add(profile)
            self.session.flush()
        return profile
