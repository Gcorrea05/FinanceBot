from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.report_service import (
    ReportService,
)


class ReportRepositoryStub:
    def __init__(
        self,
        expenses,
    ):
        self.expenses = expenses
        self.received = None

    def list_for_period(
        self,
        **kwargs,
    ):
        self.received = kwargs
        return self.expenses


def make_expense(
    *,
    expense_id,
    purchase_date,
    purchase_place,
    purchase_value,
    category,
    payment_method="Credito",
    shared_value="0.00",
    installments=None,
):
    people = (
        [
            SimpleNamespace(
                shared_value=Decimal(
                    shared_value
                )
            )
        ]
        if Decimal(
            shared_value
        ) > 0
        else []
    )

    return SimpleNamespace(
        id=expense_id,
        purchase_date=purchase_date,
        purchase_place=purchase_place,
        purchase_value=Decimal(
            purchase_value
        ),
        category=SimpleNamespace(
            name=category
        ),
        payment_method=SimpleNamespace(
            name=payment_method
        ),
        is_installment=bool(
            installments
        ),
        people=people,
        installments=(
            installments or []
        ),
    )


def installment(
    number,
    due_date,
    value,
    *,
    paid=False,
):
    return SimpleNamespace(
        installment_number=number,
        total_installments=3,
        due_date=due_date,
        installment_value=Decimal(
            value
        ),
        is_paid=paid,
    )


def test_builds_monthly_and_category_report():
    market = make_expense(
        expense_id=1,
        purchase_date=datetime(
            2026,
            7,
            5,
        ),
        purchase_place="Mercado Central",
        purchase_value="100.00",
        category="Mercado",
        payment_method="Pix",
        shared_value="40.00",
    )

    notebook = make_expense(
        expense_id=2,
        purchase_date=datetime(
            2026,
            6,
            10,
        ),
        purchase_place="Loja Tech",
        purchase_value="300.00",
        category="Eletronicos",
        shared_value="60.00",
        installments=[
            installment(
                1,
                date(
                    2026,
                    6,
                    15,
                ),
                "100.00",
                paid=True,
            ),
            installment(
                2,
                date(
                    2026,
                    7,
                    15,
                ),
                "100.00",
            ),
            installment(
                3,
                date(
                    2026,
                    8,
                    15,
                ),
                "100.00",
            ),
        ],
    )

    repository = ReportRepositoryStub(
        [
            market,
            notebook,
        ]
    )
    service = ReportService(
        repository
    )

    report = service.get_overview(
        start_year=2026,
        start_month=7,
        end_year=2026,
        end_month=8,
    )

    assert report.total_spent == Decimal(
        "220.00"
    )
    assert report.monthly_average == Decimal(
        "110.00"
    )
    assert [
        item.total
        for item in report.monthly
    ] == [
        Decimal("140.00"),
        Decimal("80.00"),
    ]
    assert report.highest_month.label == "Jul/26"
    assert report.categories[0].name == "Eletronicos"
    assert report.categories[0].total == Decimal(
        "160.00"
    )
    assert report.merchants[0].name == "Loja Tech"
    assert report.installment_commitment == Decimal(
        "160.00"
    )
    assert report.installments[0].pending_installments == 2
    assert report.installments[0].next_due_date == date(
        2026,
        7,
        15,
    )
    assert repository.received["start_month"] == 7


def test_rejects_inverted_or_oversized_period():
    service = ReportService(
        ReportRepositoryStub([])
    )

    with pytest.raises(
        ValueError,
        match="periodo inicial",
    ):
        service.get_overview(
            start_year=2026,
            start_month=8,
            end_year=2026,
            end_month=7,
        )

    with pytest.raises(
        ValueError,
        match="24 meses",
    ):
        service.get_overview(
            start_year=2024,
            start_month=1,
            end_year=2026,
            end_month=2,
        )
