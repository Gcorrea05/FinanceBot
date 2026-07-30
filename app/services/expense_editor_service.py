
from app.database.models import (
    Expense,
    ExpenseInstallment,
    ExpensePerson,
)
from app.domain.expense_validator import ExpenseValidator
from app.domain.installment_plan import InstallmentPlanBuilder
from app.domain.shared_expense import SharedExpenseSplitter
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.person_repository import PersonRepository
from app.schemas.expense.create import ExpenseCreate
from app.services.expense_management_service import ExpenseNotFoundError
from app.services.lookup_service import LookupService


class ExpenseMutationConflictError(ValueError):
    """Raised when an expense contains financial history that must be preserved."""


class ExpenseEditorService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        lookup_service: LookupService,
        validator: ExpenseValidator,
        person_repository: PersonRepository,
        installment_builder: InstallmentPlanBuilder,
        shared_splitter: SharedExpenseSplitter,
    ):
        self.expense_repository = expense_repository
        self.lookup_service = lookup_service
        self.validator = validator
        self.person_repository = person_repository
        self.installment_builder = installment_builder
        self.shared_splitter = shared_splitter

    def update(
        self,
        expense_id: int,
        data: ExpenseCreate,
    ) -> Expense:
        expense = self.expense_repository.get_detailed_by_id(expense_id)

        if expense is None:
            raise ExpenseNotFoundError(
                f"Expense {expense_id} was not found."
            )

        self._ensure_mutable(expense)
        validated = self.validator.validate(data)

        category = self.lookup_service.get_category(validated.category)
        payment_method = self.lookup_service.get_payment_method(
            validated.payment_method
        )

        expense.purchase_date = validated.purchase_date
        expense.purchase_place = validated.purchase_place
        expense.purchase_value = validated.purchase_value
        expense.category = category
        expense.payment_method = payment_method
        expense.is_installment = validated.is_installment
        expense.is_shared = validated.is_shared
        expense.notes = validated.notes

        expense.installments.clear()
        expense.people.clear()
        self.expense_repository.session.flush()

        if validated.is_installment:
            self._attach_installments(
                expense=expense,
                total=validated.purchase_value,
                installments=validated.installments,
                first_due_date=validated.first_installment_due_date,
            )

        if validated.is_shared:
            self._attach_shared_people(
                expense=expense,
                total=validated.purchase_value,
                people=validated.shared_people,
                owner_amount=validated.owner_amount,
            )

        try:
            self.expense_repository.session.commit()
        except Exception:
            self.expense_repository.session.rollback()
            raise

        self.expense_repository.session.expire_all()
        updated = self.expense_repository.get_detailed_by_id(expense_id)

        if updated is None:
            raise RuntimeError("Updated expense could not be reloaded.")

        return updated

    @staticmethod
    def _ensure_mutable(expense: Expense) -> None:
        has_paid_installments = any(
            installment.is_paid
            for installment in expense.installments
        )
        has_settled_receivables = any(
            person.is_settled
            for person in expense.people
        )

        if has_paid_installments or has_settled_receivables:
            raise ExpenseMutationConflictError(
                "A despesa possui pagamentos ou recebimentos registrados e nao pode ser editada."
            )

    def _attach_installments(
        self,
        expense: Expense,
        total,
        installments: int,
        first_due_date,
    ) -> None:
        if first_due_date is None:
            raise RuntimeError("Data da primeira parcela ausente.")

        plan = self.installment_builder.build(
            total=total,
            installments=installments,
            first_due_date=first_due_date,
        )

        expense.installments = [
            ExpenseInstallment(
                installment_number=item.installment_number,
                total_installments=item.total_installments,
                due_date=item.due_date,
                installment_value=item.amount,
            )
            for item in plan
        ]

    def _attach_shared_people(
        self,
        expense: Expense,
        total,
        people,
        owner_amount=None,
    ) -> None:
        split = self.shared_splitter.split(
            total=total,
            people=people,
            owner_amount=owner_amount,
        )

        expense.people = [
            ExpensePerson(
                person=self.person_repository.get_or_create(
                    allocation.person_name
                ),
                shared_value=allocation.amount,
            )
            for allocation in split.allocations
        ]
