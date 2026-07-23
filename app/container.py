from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.database.session import get_session
from app.repositories.category_repository import CategoryRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.payment_method_repository import (
    PaymentMethodRepository,
)
from app.services.expense_service import ExpenseService
from app.services.lookup_service import LookupService


class Container:
    def __init__(self, session: Session):
        self.session = session

        self.expense_repository = ExpenseRepository(session)

        self.category_repository = CategoryRepository(session)

        self.payment_repository = PaymentMethodRepository(
            session
        )

        self.lookup_service = LookupService(
            category_repository=self.category_repository,
            payment_method_repository=self.payment_repository,
        )

        self.expense_service = ExpenseService(
            expense_repository=self.expense_repository,
            lookup_service=self.lookup_service,
        )


@contextmanager
def container_context() -> Iterator[Container]:
    session = get_session()

    try:
        yield Container(session)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
