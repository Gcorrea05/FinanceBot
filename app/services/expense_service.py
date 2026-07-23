from app.database.models import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense.create import ExpenseCreate

from app.services.reference_data_service import (
    ReferenceDataService,
)


class ExpenseService:

    def __init__(
        self,
        expense_repository: ExpenseRepository,
        reference_service: ReferenceDataService,
    ):
        self.expense_repository = expense_repository
        self.reference_service = reference_service

    def create_expense(
        self,
        data: ExpenseCreate,
    ):

        category = self.reference_service.get_category(
            data.category
        )

        payment = self.reference_service.get_payment_method(
            data.payment_method
        )

        expense = Expense(
            purchase_date=data.purchase_date,
            purchase_place=data.purchase_place,
            purchase_value=data.purchase_value,
            category_id=category.id,
            payment_method_id=payment.id,
            is_installment=data.is_installment,
            is_shared=data.is_shared,
            notes=data.notes,
        )

        return self.expense_repository.add(expense)