
from app.database.models import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense.create import ExpenseCreate
from app.services.lookup_service import LookupService


class ExpenseService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        lookup_service: LookupService,
    ):
        self.expense_repository = expense_repository
        self.lookup_service = lookup_service

    def create_expense(self, data: ExpenseCreate) -> Expense:
        category = self.lookup_service.get_category(
            data.category
        )

        payment_method = self.lookup_service.get_payment_method(
            data.payment_method
        )

        expense = Expense(
            purchase_date=data.purchase_date,
            purchase_place=data.purchase_place,
            purchase_value=data.purchase_value,
            category_id=category.id,
            payment_method_id=payment_method.id,
            is_installment=data.is_installment,
            is_shared=data.is_shared,
            notes=data.notes,
        )

        return self.expense_repository.add(expense)
