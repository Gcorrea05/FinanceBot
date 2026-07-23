
from sqlalchemy.orm import Session

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

        # Repositories
        self.expense_repository = ExpenseRepository(session)
        self.category_repository = CategoryRepository(session)
        self.payment_repository = PaymentMethodRepository(session)

        # Services
        self.lookup_service = LookupService(
            self.category_repository,
            self.payment_repository,
        )

        self.expense_service = ExpenseService(
            self.expense_repository,
            self.lookup_service,
        )
