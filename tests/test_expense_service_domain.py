from datetime import datetime

import pytest

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.schemas.expense.create import ExpenseCreate
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


def make_data(
    **changes,
) -> ExpenseCreate:
    values = {
        "purchase_date": datetime(
            2026,
            7,
            23,
            18,
            0,
        ),
        "purchase_place": "Loja Teste",
        "purchase_value": "R$ 1.234,56",
        "category": "Mercado",
        "payment_method": "Credito",
        "is_installment": True,
        "installments": 3,
        "is_shared": False,
        "notes": "  Compra   teste  ",
    }

    values.update(changes)

    return ExpenseCreate(**values)


def test_service_uses_validated_expense():
    repository = ExpenseRepositoryStub()

    service = ExpenseService(
        expense_repository=repository,
        lookup_service=LookupServiceStub(),
    )

    expense = service.create_expense(
        make_data()
    )

    assert expense.purchase_value == 1234.56
    assert expense.purchase_place == "Loja Teste"
    assert expense.category_id == 10
    assert expense.payment_method_id == 20
    assert expense.is_installment is True
    assert expense.notes == "Compra teste"

    assert repository.saved_expense is expense


def test_service_does_not_save_invalid_expense():
    repository = ExpenseRepositoryStub()

    service = ExpenseService(
        expense_repository=repository,
        lookup_service=LookupServiceStub(),
    )

    with pytest.raises(
        ExpenseValidationError,
    ):
        service.create_expense(
            make_data(
                purchase_value=0
            )
        )

    assert repository.saved_expense is None
