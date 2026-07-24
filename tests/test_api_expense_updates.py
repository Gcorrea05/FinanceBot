from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.expense_editor_service import ExpenseMutationConflictError


def make_expense():
    return SimpleNamespace(
        id=10,
        purchase_date=datetime(2026, 7, 24, 10, 0),
        purchase_place="Mercado Central",
        purchase_value=150.75,
        category=SimpleNamespace(name="Mercado"),
        payment_method=SimpleNamespace(name="Pix"),
        is_installment=False,
        is_shared=False,
        notes=None,
        created_at=datetime(2026, 7, 24, 10, 1),
        updated_at=datetime(2026, 7, 24, 10, 2),
        installments=[],
        people=[],
    )


class EditorStub:
    def __init__(self, conflict=False):
        self.conflict = conflict
        self.received = None

    def update(self, expense_id, data):
        if self.conflict:
            raise ExpenseMutationConflictError(
                "A despesa possui historico financeiro."
            )
        self.received = (expense_id, data)
        return make_expense()


def make_client(editor):
    application = create_app()
    application.dependency_overrides[get_container] = lambda: SimpleNamespace(
        expense_editor_service=editor
    )
    return TestClient(application)


def payload():
    return {
        "purchase_date": "2026-07-24T10:00:00",
        "purchase_place": "Mercado Central",
        "purchase_value": "150.75",
        "category": "Mercado",
        "payment_method": "Pix",
        "is_installment": False,
        "installments": 1,
        "first_installment_due_date": None,
        "is_shared": False,
        "shared_people": [],
        "notes": None,
    }


def test_updates_expense_with_put():
    editor = EditorStub()
    client = make_client(editor)

    response = client.put(
        "/api/v1/expenses/10",
        json=payload(),
    )

    assert response.status_code == 200
    assert response.json()["id"] == 10
    assert editor.received[0] == 10
    assert editor.received[1].purchase_place == "Mercado Central"


def test_returns_conflict_for_locked_expense():
    client = make_client(EditorStub(conflict=True))

    response = client.put(
        "/api/v1/expenses/10",
        json=payload(),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "expense_mutation_conflict"
