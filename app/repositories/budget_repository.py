from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Budget
from app.repositories.base_repository import BaseRepository


class BudgetRepository(BaseRepository[Budget]):

    def __init__(self, session: Session):
        super().__init__(session)

    def get_budget(self, month: int, year: int):

        return self.session.scalar(
            select(Budget)
            .where(Budget.month == month)
            .where(Budget.year == year)
        )