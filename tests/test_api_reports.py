from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.report_service import (
    CategoryReportItem,
    InstallmentReportItem,
    MerchantReportItem,
    MonthlyReportPoint,
    ReportOverview,
    ReportPeriod,
)


class ReportServiceStub:
    def __init__(self):
        self.received = None

    def get_overview(
        self,
        **kwargs,
    ):
        self.received = kwargs

        month = MonthlyReportPoint(
            year=2026,
            month=7,
            label="Jul/26",
            total=Decimal("500.00"),
        )

        return ReportOverview(
            period=ReportPeriod(
                start_year=2026,
                start_month=7,
                end_year=2026,
                end_month=7,
            ),
            total_spent=Decimal(
                "500.00"
            ),
            monthly_average=Decimal(
                "500.00"
            ),
            transactions=3,
            highest_month=month,
            installment_commitment=Decimal(
                "200.00"
            ),
            monthly=[month],
            categories=[
                CategoryReportItem(
                    name="Mercado",
                    total=Decimal(
                        "500.00"
                    ),
                    percentage=Decimal(
                        "100.00"
                    ),
                )
            ],
            merchants=[
                MerchantReportItem(
                    name="Mercado Central",
                    total=Decimal(
                        "500.00"
                    ),
                    transactions=3,
                )
            ],
            installments=[
                InstallmentReportItem(
                    expense_id=10,
                    purchase_place=(
                        "Loja Tech"
                    ),
                    category=(
                        "Eletronicos"
                    ),
                    payment_method=(
                        "Credito"
                    ),
                    purchase_value=Decimal(
                        "600.00"
                    ),
                    owner_total=Decimal(
                        "600.00"
                    ),
                    total_installments=3,
                    paid_installments=2,
                    pending_installments=1,
                    next_due_date=date(
                        2026,
                        8,
                        10,
                    ),
                    remaining_amount=Decimal(
                        "200.00"
                    ),
                )
            ],
        )


def make_client():
    application = create_app()
    service = ReportServiceStub()

    application.dependency_overrides[
        get_container
    ] = lambda: SimpleNamespace(
        report_service=service
    )

    return (
        TestClient(application),
        service,
    )


def test_get_report_overview():
    client, service = make_client()

    response = client.get(
        (
            "/api/v1/reports/overview"
            "?start_year=2026"
            "&start_month=7"
            "&end_year=2026"
            "&end_month=7"
            "&category=Mercado"
        )
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_spent"] == "500.00"
    assert body["monthly"][0]["label"] == "Jul/26"
    assert body["categories"][0]["percentage"] == "100.00"
    assert body["installments"][0]["pending_installments"] == 1
    assert service.received["category"] == "Mercado"


def test_report_query_validation():
    client, _ = make_client()

    response = client.get(
        (
            "/api/v1/reports/overview"
            "?start_year=2026"
            "&start_month=13"
            "&end_year=2026"
            "&end_month=7"
        )
    )

    assert response.status_code == 422
