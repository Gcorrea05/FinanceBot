from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from app.services.expense_query_service import (
    ExpenseQueryService,
)


class ExpenseRepositoryStub:
    def __init__(self):
        self.received_limit = None

    def list_recent(self, limit):
        self.received_limit = limit

        return [
            SimpleNamespace(
                id=10,
                purchase_date=datetime(
                    2026,
                    7,
                    23,
                    18,
                    30,
                ),
                purchase_place="Mercado Central",
                purchase_value=150.755,
                category=SimpleNamespace(
                    name="Mercado"
                ),
                payment_method=SimpleNamespace(
                    name="Pix"
                ),
                is_installment=False,
                is_shared=True,
            )
        ]


def test_list_recent_maps_expense_data():
    repository = ExpenseRepositoryStub()
    service = ExpenseQueryService(
        repository
    )

    result = service.list_recent(
        limit=5
    )

    assert repository.received_limit == 5
    assert len(result) == 1

    expense = result[0]

    assert expense.expense_id == 10
    assert (
        expense.purchase_place
        == "Mercado Central"
    )
    assert (
        expense.purchase_value
        == Decimal("150.76")
    )
    assert expense.category_name == "Mercado"
    assert expense.payment_method_name == "Pix"
    assert expense.is_shared is True
