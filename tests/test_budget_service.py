from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from types import SimpleNamespace

from app.services.budget_service import (
    BudgetService,
)


class BudgetRepositoryStub:
    def __init__(self):
        self.budget = None

    def get_by_period(
        self,
        *,
        year,
        month,
    ):
        del year, month
        return self.budget

    def save_plan(self, **values):
        self.budget = SimpleNamespace(
            **values
        )
        return self.budget


class ExpenseRepositoryStub:
    def __init__(self, expenses):
        self.expenses = expenses

    def list_for_period(
        self,
        *,
        year,
        month,
    ):
        del year, month
        return self.expenses


def test_budget_counts_only_owner_share():
    expense = SimpleNamespace(
        purchase_value=Decimal("300.00"),
        is_installment=False,
        purchase_date=datetime(
            2026,
            7,
            10,
        ),
        people=[
            SimpleNamespace(
                shared_value=Decimal("80.00")
            ),
            SimpleNamespace(
                shared_value=Decimal("50.00")
            ),
        ],
        installments=[],
    )

    budget_repository = BudgetRepositoryStub()
    service = BudgetService(
        budget_repository=budget_repository,
        expense_repository=ExpenseRepositoryStub(
            [expense]
        ),
    )

    overview = service.save_plan(
        year=2026,
        month=7,
        monthly_income="5000.00",
        reserve_target="1000.00",
        spending_limit="3000.00",
    )

    assert overview.spent == Decimal(
        "170.00"
    )
    assert overview.remaining == Decimal(
        "2830.00"
    )


def test_budget_uses_installment_due_in_period():
    expense = SimpleNamespace(
        purchase_value=Decimal("1200.00"),
        is_installment=True,
        purchase_date=datetime(
            2026,
            5,
            10,
        ),
        people=[],
        installments=[
            SimpleNamespace(
                due_date=date(
                    2026,
                    7,
                    10,
                ),
                installment_value=Decimal(
                    "100.00"
                ),
            ),
            SimpleNamespace(
                due_date=date(
                    2026,
                    8,
                    10,
                ),
                installment_value=Decimal(
                    "100.00"
                ),
            ),
        ],
    )

    service = BudgetService(
        budget_repository=BudgetRepositoryStub(),
        expense_repository=ExpenseRepositoryStub(
            [expense]
        ),
    )

    overview = service.get_overview(
        year=2026,
        month=7,
        today=date(
            2026,
            7,
            15,
        ),
    )

    assert overview.spent == Decimal(
        "100.00"
    )
    assert overview.configured is False
    assert overview.remaining_days == 17
