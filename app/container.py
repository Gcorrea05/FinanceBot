from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.database.session import get_session
from app.domain.expense_validator import (
    ExpenseValidator,
)
from app.domain.installment_plan import (
    InstallmentPlanBuilder,
)
from app.domain.shared_expense import (
    SharedExpenseSplitter,
)
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.repositories.expense_repository import (
    ExpenseRepository,
)
from app.repositories.payment_method_repository import (
    PaymentMethodRepository,
)
from app.repositories.person_repository import (
    PersonRepository,
)
from app.repositories.receivable_repository import (
    ReceivableRepository,
)
from app.services.expense_service import ExpenseService
from app.services.lookup_service import LookupService
from app.services.receivable_service import (
    ReceivableService,
)


class Container:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

        self.expense_repository = ExpenseRepository(
            session
        )

        self.category_repository = CategoryRepository(
            session
        )

        self.payment_repository = (
            PaymentMethodRepository(session)
        )

        self.person_repository = PersonRepository(
            session
        )

        self.receivable_repository = (
            ReceivableRepository(session)
        )

        self.lookup_service = LookupService(
            category_repository=(
                self.category_repository
            ),
            payment_method_repository=(
                self.payment_repository
            ),
        )

        self.expense_validator = ExpenseValidator()
        self.installment_builder = (
            InstallmentPlanBuilder()
        )
        self.shared_splitter = (
            SharedExpenseSplitter()
        )

        self.expense_service = ExpenseService(
            expense_repository=(
                self.expense_repository
            ),
            lookup_service=self.lookup_service,
            validator=self.expense_validator,
            person_repository=(
                self.person_repository
            ),
            installment_builder=(
                self.installment_builder
            ),
            shared_splitter=(
                self.shared_splitter
            ),
        )

        self.receivable_service = ReceivableService(
            receivable_repository=(
                self.receivable_repository
            ),
            person_repository=(
                self.person_repository
            ),
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
