from datetime import date, datetime
from decimal import Decimal

from app.database.models import Person
from app.schemas.expense.create import ExpenseCreate
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)
from app.services.expense_service import ExpenseService


class NamedEntity:
    def __init__(
        self,
        entity_id: int,
        name: str,
    ):
        self.id = entity_id
        self.name = name


class LookupServiceStub:
    def get_category(self, name):
        return NamedEntity(
            entity_id=10,
            name=name,
        )

    def get_payment_method(self, name):
        return NamedEntity(
            entity_id=20,
            name=name,
        )


class ExpenseRepositoryStub:
    def __init__(self):
        self.saved_expense = None

    def add(self, expense):
        self.saved_expense = expense
        return expense


class PersonRepositoryStub:
    def __init__(self):
        self.people = {}

    def get_or_create(self, name):
        normalized = (
            name.strip().casefold()
        )

        if normalized not in self.people:
            self.people[normalized] = Person(
                name=name,
                normalized_name=normalized,
            )

        return self.people[normalized]


def test_service_builds_complete_expense_graph():
    repository = ExpenseRepositoryStub()
    person_repository = PersonRepositoryStub()

    service = ExpenseService(
        expense_repository=repository,
        lookup_service=LookupServiceStub(),
        person_repository=person_repository,
    )

    expense = service.create_expense(
        ExpenseCreate(
            purchase_date=datetime(
                2026,
                7,
                24,
                10,
                0,
            ),
            purchase_place="Hotel Teste",
            purchase_value="1000,00",
            category="Viagem",
            payment_method="Credito",
            is_installment=True,
            installments=3,
            first_installment_due_date=date(
                2026,
                8,
                10,
            ),
            is_shared=True,
            shared_people=(
                SharedPersonCreate(
                    name="Ana",
                    amount="250,00",
                ),
                SharedPersonCreate(
                    name="Bruno",
                    amount="150,00",
                ),
            ),
            notes="Viagem compartilhada",
        )
    )

    assert repository.saved_expense is expense

    assert len(expense.installments) == 3

    assert sum(
        (
            item.installment_value
            for item in expense.installments
        ),
        start=Decimal("0.00"),
    ) == Decimal("1000.00")

    assert len(expense.people) == 2

    assert sum(
        (
            item.shared_value
            for item in expense.people
        ),
        start=Decimal("0.00"),
    ) == Decimal("400.00")
