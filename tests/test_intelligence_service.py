from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

from app.services.intelligence_service import IntelligenceService
from app.services.report_service import (
    CategoryReportItem,
    MonthlyReportPoint,
    ReportOverview,
    ReportPeriod,
)


class RepositoryStub:
    def __init__(self, expenses):
        self.expenses = expenses

    def list_for_period(self, **kwargs):
        del kwargs
        return self.expenses


class ReportServiceStub:
    def get_overview(self, *, start_year, start_month, end_year, end_month, **kwargs):
        del kwargs
        if (start_year, start_month) == (end_year, end_month):
            monthly = [MonthlyReportPoint(year=end_year, month=end_month, label='Jul/26', total=Decimal('900.00'))]
            categories = [CategoryReportItem(name='Mercado', total=Decimal('500.00'), percentage=Decimal('55.56'))]
        else:
            monthly = [
                MonthlyReportPoint(year=2026, month=2, label='Fev/26', total=Decimal('600.00')),
                MonthlyReportPoint(year=2026, month=3, label='Mar/26', total=Decimal('700.00')),
                MonthlyReportPoint(year=2026, month=4, label='Abr/26', total=Decimal('800.00')),
                MonthlyReportPoint(year=2026, month=5, label='Mai/26', total=Decimal('750.00')),
                MonthlyReportPoint(year=2026, month=6, label='Jun/26', total=Decimal('650.00')),
                MonthlyReportPoint(year=2026, month=7, label='Jul/26', total=Decimal('900.00')),
            ]
            categories = []
        return ReportOverview(
            period=ReportPeriod(start_year=start_year, start_month=start_month, end_year=end_year, end_month=end_month),
            total_spent=sum((item.total for item in monthly), Decimal('0.00')),
            monthly_average=Decimal('0.00'),
            transactions=5,
            highest_month=max(monthly, key=lambda item: item.total),
            installment_commitment=Decimal('300.00'),
            monthly=monthly,
            categories=categories,
            merchants=[],
            installments=[],
        )


    def contribution_for_month(
        self,
        *,
        expense,
        year,
        month,
    ):
        purchase_total = Decimal(
            str(expense.purchase_value)
        )

        shared_total = sum(
            (
                Decimal(
                    str(relation.shared_value)
                )
                for relation in getattr(
                    expense,
                    "people",
                    [],
                )
            ),
            Decimal("0.00"),
        )

        owner_total = max(
            purchase_total - shared_total,
            Decimal("0.00"),
        )

        if not getattr(
            expense,
            "is_installment",
            False,
        ):
            expense_period = (
                expense.purchase_date.year,
                expense.purchase_date.month,
            )

            if expense_period == (year, month):
                return owner_total

            return Decimal("0.00")

        if purchase_total <= 0:
            return Decimal("0.00")

        owner_ratio = (
            owner_total / purchase_total
        )

        contribution = sum(
            (
                Decimal(
                    str(
                        installment.installment_value
                    )
                )
                * owner_ratio
                for installment in getattr(
                    expense,
                    "installments",
                    [],
                )
                if (
                    installment.due_date.year,
                    installment.due_date.month,
                ) == (year, month)
            ),
            Decimal("0.00"),
        )

        return contribution.quantize(
            Decimal("0.01")
        )


class BudgetServiceStub:
    def get_overview(self, **kwargs):
        del kwargs
        return SimpleNamespace(
            status='healthy',
            usage_percent=Decimal('45.00'),
            spending_limit=Decimal('2000.00'),
        )


def expense(expense_id, value, day, place='Mercado Central'):
    return SimpleNamespace(
        id=expense_id,
        purchase_date=datetime(2026, 7 if expense_id >= 5 else expense_id + 1, day),
        purchase_place=place,
        purchase_value=Decimal(value),
        category=SimpleNamespace(name='Mercado'),
        is_installment=False,
        installments=[],
        people=[],
    )


def test_builds_explainable_intelligence():
    expenses = [
        expense(1, '100.00', 5),
        expense(2, '110.00', 5),
        expense(3, '90.00', 5),
        expense(4, '105.00', 5),
        expense(5, '600.00', 10),
        expense(6, '100.00', 12),
        expense(7, '100.00', 12),
    ]
    service = IntelligenceService(
        repository=RepositoryStub(expenses),
        report_service=ReportServiceStub(),
        budget_service=BudgetServiceStub(),
    )
    overview = service.get_overview(year=2026, month=7, today=date(2026, 7, 20))
    assert overview.summary.current_total == Decimal('900.00')
    assert overview.summary.historical_average == Decimal('700.00')
    assert overview.summary.forecast_total >= overview.summary.current_total
    assert overview.anomalies[0].expense_id == 5
    assert any(item.code == 'category_concentration' for item in overview.insights)
