from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container


class LookupStub:
    def list_category_names(self):
        return [
            "Alimentacao",
            "Mercado",
        ]

    def list_payment_method_names(self):
        return [
            "Pix",
            "Credito",
        ]


def test_reference_endpoints():
    application = create_app()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        lookup_service=LookupStub()
    )

    client = TestClient(application)

    categories = client.get(
        "/api/v1/references/categories"
    )

    payments = client.get(
        (
            "/api/v1/references/"
            "payment-methods"
        )
    )

    assert categories.status_code == 200
    assert categories.json()["items"] == [
        {"name": "Alimentacao"},
        {"name": "Mercado"},
    ]

    assert payments.status_code == 200
    assert payments.json()["items"] == [
        {"name": "Pix"},
        {"name": "Credito"},
    ]
