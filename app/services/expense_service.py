from app.database.models import Expense
from app.domain.expense_validator import (
    ExpenseValidator,
)
from app.repositories.expense_repository import (
    ExpenseRepository,
)
from app.schemas.expense.create import ExpenseCreate
from app.services.lookup_service import LookupService


class ExpenseService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        lookup_service: LookupService,
        validator: ExpenseValidator | None = None,
    ):
        self.expense_repository = expense_repository
        self.lookup_service = lookup_service
        self.validator = (
            validator
            if validator is not None
            else ExpenseValidator()
        )

    def create_expense(
        self,
        data: ExpenseCreate,
    ) -> Expense:
        validated = self.validator.validate(data)

        category = self.lookup_service.get_category(
            validated.category
        )

        payment_method = (
            self.lookup_service
            .get_payment_method(
                validated.payment_method
            )
        )

        expense = Expense(
            purchase_date=validated.purchase_date,
            purchase_place=validated.purchase_place,
            purchase_value=float(
                validated.purchase_value
            ),
            category_id=category.id,
            payment_method_id=payment_method.id,
            is_installment=(
                validated.is_installment
            ),
            is_shared=validated.is_shared,
            notes=validated.notes,
        )

        return self.expense_repository.add(
            expense
        )
