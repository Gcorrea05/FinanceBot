from app.database.models import (
    Expense,
    ExpenseInstallment,
    ExpensePerson,
)
from app.domain.expense_validator import (
    ExpenseValidator,
)
from app.domain.installment_plan import (
    InstallmentPlanBuilder,
)
from app.domain.shared_expense import (
    SharedExpenseSplitter,
)
from app.repositories.expense_repository import (
    ExpenseRepository,
)
from app.repositories.person_repository import (
    PersonRepository,
)
from app.schemas.expense.create import ExpenseCreate
from app.services.lookup_service import LookupService


class ExpenseService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        lookup_service: LookupService,
        validator: ExpenseValidator | None = None,
        person_repository: PersonRepository | None = None,
        installment_builder: (
            InstallmentPlanBuilder | None
        ) = None,
        shared_splitter: (
            SharedExpenseSplitter | None
        ) = None,
    ):
        self.expense_repository = expense_repository
        self.lookup_service = lookup_service
        self.validator = (
            validator
            if validator is not None
            else ExpenseValidator()
        )
        self.person_repository = person_repository
        self.installment_builder = (
            installment_builder
            if installment_builder is not None
            else InstallmentPlanBuilder()
        )
        self.shared_splitter = (
            shared_splitter
            if shared_splitter is not None
            else SharedExpenseSplitter()
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

        if validated.is_installment:
            self._attach_installments(
                expense=expense,
                total=validated.purchase_value,
                installments=validated.installments,
                first_due_date=(
                    validated
                    .first_installment_due_date
                ),
            )

        if validated.is_shared:
            self._attach_shared_people(
                expense=expense,
                total=validated.purchase_value,
                people=validated.shared_people,
            )

        return self.expense_repository.add(
            expense
        )

    def _attach_installments(
        self,
        expense: Expense,
        total,
        installments: int,
        first_due_date,
    ) -> None:
        if first_due_date is None:
            raise RuntimeError(
                "Data da primeira parcela ausente."
            )

        plan = self.installment_builder.build(
            total=total,
            installments=installments,
            first_due_date=first_due_date,
        )

        expense.installments = [
            ExpenseInstallment(
                installment_number=(
                    item.installment_number
                ),
                total_installments=(
                    item.total_installments
                ),
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
    ) -> None:
        if self.person_repository is None:
            raise RuntimeError(
                (
                    "PersonRepository nao foi "
                    "configurado no ExpenseService."
                )
            )

        split = self.shared_splitter.split(
            total=total,
            people=people,
        )

        expense.people = [
            ExpensePerson(
                person=(
                    self.person_repository
                    .get_or_create(
                        allocation.person_name
                    )
                ),
                shared_value=allocation.amount,
            )
            for allocation in split.allocations
        ]
