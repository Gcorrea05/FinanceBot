
from datetime import datetime

import pytest

from app.database.models import Category, PaymentMethod
from app.schemas.expense.create import ExpenseCreate
from app.services.expense_service import ExpenseService
from app.services.lookup_service import (
    LookupNotFoundError,
    LookupService,
)


class InMemoryRepository:
    def __init__(self, items):
        self.items = items

    def get_all(self):
        return list(self.items)


class ExpenseRepositoryStub:
    def __init__(self):
        self.saved_expense = None

    def add(self, expense):
        self.saved_expense = expense
        return expense


@pytest.fixture
def lookup_service():
    categories = [
        Category(id=1, name="Alimenta\u00e7\u00e3o"),
        Category(id=2, name="Mercado"),
        Category(id=3, name="Transporte"),
    ]

    payment_methods = [
        PaymentMethod(id=1, name="Pix"),
        PaymentMethod(id=2, name="D\u00e9bito"),
        PaymentMethod(id=3, name="Cr\u00e9dito"),
        PaymentMethod(id=4, name="Dinheiro"),
    ]

    return LookupService(
        category_repository=InMemoryRepository(categories),
        payment_method_repository=InMemoryRepository(
            payment_methods
        ),
    )


def test_get_category_without_accent_and_with_extra_spaces(
    lookup_service,
):
    category = lookup_service.get_category(
        "  ALIMENTACAO  "
    )

    assert category.name == "Alimenta\u00e7\u00e3o"


def test_get_category_by_alias(lookup_service):
    category = lookup_service.get_category("supermercado")

    assert category.name == "Mercado"


def test_get_payment_method_by_alias(lookup_service):
    payment_method = lookup_service.get_payment_method(
        "cart\u00e3o de cr\u00e9dito"
    )

    assert payment_method.name == "Cr\u00e9dito"


def test_lookup_error_contains_suggestion(lookup_service):
    with pytest.raises(
        LookupNotFoundError,
        match="Alimenta\u00e7\u00e3o",
    ):
        lookup_service.get_category("alimentcao")


def test_list_reference_names(lookup_service):
    assert lookup_service.list_category_names() == [
        "Alimenta\u00e7\u00e3o",
        "Mercado",
        "Transporte",
    ]

    assert lookup_service.list_payment_method_names() == [
        "Cr\u00e9dito",
        "D\u00e9bito",
        "Dinheiro",
        "Pix",
    ]


def test_expense_service_uses_normalized_lookup(
    lookup_service,
):
    expense_repository = ExpenseRepositoryStub()

    expense_service = ExpenseService(
        expense_repository=expense_repository,
        lookup_service=lookup_service,
    )

    expense_data = ExpenseCreate(
        purchase_date=datetime(2026, 7, 22, 20, 30),
        purchase_place="Supermercado Teste",
        purchase_value=150.75,
        category="supermercado",
        payment_method="cartao de credito",
    )

    expense = expense_service.create_expense(
        expense_data
    )

    assert expense.category_id == 2
    assert expense.payment_method_id == 3
    assert expense_repository.saved_expense is expense
