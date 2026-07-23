from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Expense
from app.repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_id(self, expense_id: int):

        return self.session.get(Expense, expense_id)

    def get_all(self):

        return self.session.scalars(
            select(Expense)
        ).all()

    def get_current_month(self, month: int, year: int):

        return self.session.scalars(
            select(Expense)
        ).all()