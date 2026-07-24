from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.receivable_service import (
    ReceivableItem,
    ReceivableSummary,
)


class ReceivableServiceStub:
    def list_open_summary(self):
        return [
            ReceivableSummary(
                person_id=1,
                person_name="Tomas",
                total=Decimal("70.00"),
                pending_count=1,
            ),
            ReceivableSummary(
                person_id=2,
                person_name="Sofia",
                total=Decimal("50.50"),
                pending_count=1,
            ),
        ]

    def list_open_for_person_id(
        self,
        person_id,
    ):
        return [
            ReceivableItem(
                receivable_id=10,
                expense_id=20,
                person_id=person_id,
                person_name="Tomas",
                purchase_place="Mercado",
                purchase_date=datetime(
                    2026,
                    7,
                    24,
                    10,
                    0,
                ),
                amount=Decimal("70.00"),
            )
        ]

    def settle(self, receivable_id):
        return SimpleNamespace(
            id=receivable_id,
            is_settled=True,
            settled_at=datetime(
                2026,
                7,
                24,
                12,
                0,
            ),
        )


def make_client():
    application = create_app()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        receivable_service=(
            ReceivableServiceStub()
        )
    )

    return TestClient(application)


def test_receivable_summary():
    response = make_client().get(
        "/api/v1/receivables"
    )

    assert response.status_code == 200
    assert (
        response.json()["total_general"]
        == "120.50"
    )
    assert len(
        response.json()["people"]
    ) == 2


def test_receivable_detail_and_settle():
    client = make_client()

    detail = client.get(
        (
            "/api/v1/receivables/"
            "people/1"
        )
    )

    settled = client.post(
        (
            "/api/v1/receivables/"
            "10/settle"
        )
    )

    assert detail.status_code == 200
    assert detail.json()["total"] == "70.00"
    assert settled.status_code == 200
    assert (
        settled.json()["is_settled"]
        is True
    )
