from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.expense_editor_service import (
    ExpenseEditorService,
    ExpenseMutationConflictError,
)
from app.services.expense_management_service import ExpenseNotFoundError


class SessionStub:
    def __init__(self):
        self.flushed = False
        self.committed = False
        self.rolled_back = False
        self.expired = False

    def flush(self):
        self.flushed = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def expire_all(self):
        self.expired = True


class RepositoryStub:
    def __init__(self, expense):
        self.expense = expense
        self.session = SessionStub()

    def get_detailed_by_id(self, expense_id):
        if self.expense is not None and self.expense.id == expense_id:
            return self.expense
        return None


class ValidatorStub:
    def validate(self, data):
        return data


class LookupStub:
    def get_category(self, name):
        return SimpleNamespace(id=10, name=name)

    def get_payment_method(self, name):
        return SimpleNamespace(id=20, name=name)


class PersonRepositoryStub:
    pass


class BuilderStub:
    pass


class SplitterStub:
    pass


def make_expense():
    return SimpleNamespace(
        id=5,
        purchase_date=datetime(2026, 7, 1, 10, 0),
        purchase_place="Antigo",
        purchase_value=10.0,
        category=SimpleNamespace(id=1, name="Outros"),
        payment_method=SimpleNamespace(id=1, name="Pix"),
        is_installment=False,
        is_shared=False,
        notes=None,
        installments=[],
        people=[],
    )


def make_validated():
    return SimpleNamespace(
        purchase_date=datetime(2026, 7, 24, 12, 0),
        purchase_place="Mercado Central",
        purchase_value=Decimal("150.75"),
        category="Mercado",
        payment_method="Credito",
        is_installment=False,
        installments=1,
        first_installment_due_date=None,
        is_shared=False,
        shared_people=(),
        notes="Compra mensal",
    )


def make_service(expense):
    return ExpenseEditorService(
        expense_repository=RepositoryStub(expense),
        lookup_service=LookupStub(),
        validator=ValidatorStub(),
        person_repository=PersonRepositoryStub(),
        installment_builder=BuilderStub(),
        shared_splitter=SplitterStub(),
    )


def test_updates_mutable_expense():
    expense = make_expense()
    service = make_service(expense)

    updated = service.update(5, make_validated())

    assert updated.purchase_place == "Mercado Central"
    assert updated.purchase_value == 150.75
    assert updated.category.name == "Mercado"
    assert updated.payment_method.name == "Credito"
    assert updated.notes == "Compra mensal"
    assert service.expense_repository.session.flushed is True
    assert service.expense_repository.session.committed is True
    assert service.expense_repository.session.expired is True


def test_rejects_expense_with_settled_receivable():
    expense = make_expense()
    expense.people = [SimpleNamespace(is_settled=True)]
    service = make_service(expense)

    with pytest.raises(ExpenseMutationConflictError):
        service.update(5, make_validated())


def test_raises_when_expense_does_not_exist():
    service = make_service(None)

    with pytest.raises(ExpenseNotFoundError):
        service.update(999, make_validated())
