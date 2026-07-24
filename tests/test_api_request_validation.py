from fastapi.testclient import TestClient

from app.api.app import create_app


def test_installment_requires_due_date():
    response = TestClient(
        create_app()
    ).post(
        "/api/v1/expenses",
        json={
            "purchase_date": (
                "2026-07-24T10:00:00"
            ),
            "purchase_place": "Loja",
            "purchase_value": "500.00",
            "category": "Outros",
            "payment_method": "Credito",
            "is_installment": True,
            "installments": 5,
        },
    )

    assert response.status_code == 422


def test_shared_expense_requires_people():
    response = TestClient(
        create_app()
    ).post(
        "/api/v1/expenses",
        json={
            "purchase_date": (
                "2026-07-24T10:00:00"
            ),
            "purchase_place": "Loja",
            "purchase_value": "500.00",
            "category": "Outros",
            "payment_method": "Pix",
            "is_shared": True,
            "shared_people": [],
        },
    )

    assert response.status_code == 422
