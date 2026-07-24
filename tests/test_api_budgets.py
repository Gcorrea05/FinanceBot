from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.budget_service import (
    BudgetOverview,
)


class BudgetServiceStub:
    def __init__(self):
        self.saved = None

    def get_overview(
        self,
        *,
        year,
        month,
    ):
        return self._overview(
            year=year,
            month=month,
        )

    def save_plan(
        self,
        **values,
    ):
        self.saved = values

        return self._overview(
            year=values["year"],
            month=values["month"],
        )

    @staticmethod
    def _overview(
        *,
        year,
        month,
    ):
        return BudgetOverview(
            year=year,
            month=month,
            configured=True,
            monthly_income=Decimal(
                "5000.00"
            ),
            reserve_target=Decimal(
                "1000.00"
            ),
            spending_limit=Decimal(
                "3000.00"
            ),
            spent=Decimal(
                "1200.00"
            ),
            remaining=Decimal(
                "1800.00"
            ),
            available_after_reserve=Decimal(
                "2800.00"
            ),
            daily_limit=Decimal(
                "100.00"
            ),
            usage_percent=Decimal(
                "40.00"
            ),
            remaining_days=18,
            status="healthy",
        )


def make_client():
    application = create_app()
    service = BudgetServiceStub()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        budget_service=service
    )

    return (
        TestClient(application),
        service,
    )


def test_get_budget_overview():
    client, _ = make_client()

    response = client.get(
        "/api/v1/budgets/2026/7"
    )

    assert response.status_code == 200
    assert response.json()["configured"] is True
    assert response.json()["spent"] == "1200.00"


def test_save_budget_plan():
    client, service = make_client()

    response = client.put(
        "/api/v1/budgets/2026/7",
        json={
            "monthly_income": "5000.00",
            "reserve_target": "1000.00",
            "spending_limit": "3000.00",
        },
    )

    assert response.status_code == 200
    assert service.saved == {
        "year": 2026,
        "month": 7,
        "monthly_income": Decimal(
            "5000.00"
        ),
        "reserve_target": Decimal(
            "1000.00"
        ),
        "spending_limit": Decimal(
            "3000.00"
        ),
    }
