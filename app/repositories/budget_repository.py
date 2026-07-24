from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Budget
from app.repositories.base_repository import BaseRepository


class BudgetRepository(
    BaseRepository[Budget]
):
    def __init__(
        self,
        session: Session,
    ):
        super().__init__(session)

    def get_by_period(
        self,
        *,
        year: int,
        month: int,
    ) -> Budget | None:
        statement = select(Budget).where(
            Budget.year == year,
            Budget.month == month,
        )

        return self.session.scalar(
            statement
        )

    def save_plan(
        self,
        *,
        year: int,
        month: int,
        monthly_income,
        reserve_target,
        spending_limit,
    ) -> Budget:
        budget = self.get_by_period(
            year=year,
            month=month,
        )

        if budget is None:
            budget = Budget(
                year=year,
                month=month,
                monthly_income=monthly_income,
                reserve_target=reserve_target,
                spending_limit=spending_limit,
            )

            return self.add(budget)

        budget.monthly_income = monthly_income
        budget.reserve_target = reserve_target
        budget.spending_limit = spending_limit

        updated = self.update(budget)

        if updated is None:
            raise RuntimeError(
                "Nao foi possivel atualizar o planejamento."
            )

        return updated
