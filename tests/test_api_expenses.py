from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.expense_management_service import (
    ExpensePage,
)


def make_expense():
    category = SimpleNamespace(
        name="Mercado"
    )

    payment = SimpleNamespace(
        name="Pix"
    )

    return SimpleNamespace(
        id=10,
        purchase_date=datetime(
            2026,
            7,
            24,
            10,
            0,
        ),
        purchase_place="Mercado Central",
        purchase_value=150.75,
        category=category,
        payment_method=payment,
        is_installment=False,
        is_shared=False,
        notes=None,
        created_at=datetime(
            2026,
            7,
            24,
            10,
            1,
        ),
        updated_at=datetime(
            2026,
            7,
            24,
            10,
            1,
        ),
        installments=[],
        people=[],
    )


class ExpenseServiceStub:
    def create_expense(self, data):
        self.received = data
        return SimpleNamespace(id=10)


class ManagementStub:
    def __init__(self):
        self.expense = make_expense()
        self.deleted = []

    def get(self, expense_id):
        assert expense_id == 10
        return self.expense

    def list(self, **kwargs):
        self.list_kwargs = kwargs

        return ExpensePage(
            items=[self.expense],
            total=1,
            limit=kwargs["limit"],
            offset=kwargs["offset"],
        )

    def delete(self, expense_id):
        self.deleted.append(
            expense_id
        )


def make_client():
    application = create_app()
    expense_service = ExpenseServiceStub()
    management = ManagementStub()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        expense_service=expense_service,
        expense_management_service=(
            management
        ),
    )

    return (
        TestClient(application),
        expense_service,
        management,
    )


def test_create_and_read_expense():
    client, service, management = (
        make_client()
    )

    response = client.post(
        "/api/v1/expenses",
        json={
            "purchase_date": (
                "2026-07-24T10:00:00"
            ),
            "purchase_place": (
                "Mercado Central"
            ),
            "purchase_value": "150.75",
            "category": "Mercado",
            "payment_method": "Pix",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 10
    assert (
        response.json()["owner_amount"]
        == "150.75"
    )
    assert (
        service.received.purchase_place
        == "Mercado Central"
    )
    assert management.expense.id == 10


def test_list_expenses():
    client, _, management = make_client()

    response = client.get(
        (
            "/api/v1/expenses"
            "?limit=10&offset=0"
            "&month=7&year=2026"
        )
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(
        response.json()["items"]
    ) == 1
    assert management.list_kwargs == {
        "limit": 10,
        "offset": 0,
        "month": 7,
        "year": 2026,
    }


def test_delete_expense():
    client, _, management = make_client()

    response = client.delete(
        "/api/v1/expenses/10"
    )

    assert response.status_code == 204
    assert management.deleted == [10]
