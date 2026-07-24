from datetime import datetime

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.database.models import (
    Expense,
    ExpensePerson,
    Person,
)
from app.repositories.base_repository import BaseRepository


class ReceivableRepository(
    BaseRepository[ExpensePerson]
):
    def __init__(
        self,
        session: Session,
    ):
        super().__init__(session)

    def list_open_summary(self):
        statement = (
            select(
                Person.id.label("person_id"),
                Person.name.label("person_name"),
                func.sum(
                    ExpensePerson.shared_value
                ).label("total"),
                func.count(
                    ExpensePerson.id
                ).label("pending_count"),
            )
            .join(
                ExpensePerson,
                ExpensePerson.person_id
                == Person.id,
            )
            .where(
                ExpensePerson.is_settled.is_(False),
                Person.active.is_(True),
            )
            .group_by(
                Person.id,
                Person.name,
            )
            .order_by(Person.name)
        )

        return list(
            self.session.execute(
                statement
            ).all()
        )

    def list_open_for_person(
        self,
        person_id: int,
    ):
        statement = (
            select(
                ExpensePerson.id.label(
                    "receivable_id"
                ),
                Expense.id.label(
                    "expense_id"
                ),
                Person.id.label(
                    "person_id"
                ),
                Person.name.label(
                    "person_name"
                ),
                Expense.purchase_place.label(
                    "purchase_place"
                ),
                Expense.purchase_date.label(
                    "purchase_date"
                ),
                ExpensePerson.shared_value.label(
                    "amount"
                ),
            )
            .join(
                Person,
                ExpensePerson.person_id
                == Person.id,
            )
            .join(
                Expense,
                ExpensePerson.expense_id
                == Expense.id,
            )
            .where(
                ExpensePerson.person_id
                == person_id,
                ExpensePerson.is_settled.is_(False),
            )
            .order_by(
                Expense.purchase_date,
                ExpensePerson.id,
            )
        )

        return list(
            self.session.execute(
                statement
            ).all()
        )

    def get_open_by_id(
        self,
        receivable_id: int,
    ) -> ExpensePerson | None:
        statement = select(
            ExpensePerson
        ).where(
            ExpensePerson.id
            == receivable_id,
            ExpensePerson.is_settled.is_(False),
        )

        return self.session.scalar(
            statement
        )

    def settle(
        self,
        receivable_id: int,
        *,
        settled_at: datetime | None = None,
    ) -> ExpensePerson | None:
        receivable = self.get_open_by_id(
            receivable_id
        )

        if receivable is None:
            return None

        receivable.is_settled = True
        receivable.settled_at = (
            settled_at
            if settled_at is not None
            else datetime.now()
        )

        return self.update(
            receivable
        )
