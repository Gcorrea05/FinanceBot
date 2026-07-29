from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.database.models import Expense


@dataclass(frozen=True)
class DashboardComparison:
    previous_month_total: Decimal
    previous_month_change_percent: Decimal | None
    year_ago_total: Decimal
    year_ago_change_percent: Decimal | None


@dataclass(frozen=True)
class DashboardDailyPoint:
    day: int
    total: Decimal


@dataclass(frozen=True)
class DashboardOverview:
    year: int
    month: int
    spent: Decimal
    planned_income: Decimal | None
    reserve_target: Decimal | None
    budget_remaining: Decimal | None
    budget_status: str
    receivables: Decimal
    forecast_total: Decimal
    comparison: DashboardComparison
    categories: list
    daily: list[DashboardDailyPoint]
    recent_expenses: list[Expense]


class DashboardService:
    CENT = Decimal("0.01")
    HUNDRED = Decimal("100.00")

    def __init__(
        self,
        *,
        report_service,
        report_repository,
        budget_service,
        receivable_service,
        expense_management_service,
        intelligence_service,
    ):
        self.report_service = report_service
        self.report_repository = report_repository
        self.budget_service = budget_service
        self.receivable_service = receivable_service
        self.expense_management_service = expense_management_service
        self.intelligence_service = intelligence_service

    def get_overview(self, *, year: int, month: int) -> DashboardOverview:
        current = self.report_service.get_overview(
            start_year=year,
            start_month=month,
            end_year=year,
            end_month=month,
        )
        previous_year, previous_month = self._shift_month(year, month, -1)
        previous = self.report_service.get_overview(
            start_year=previous_year,
            start_month=previous_month,
            end_year=previous_year,
            end_month=previous_month,
        )
        year_ago = self.report_service.get_overview(
            start_year=year - 1,
            start_month=month,
            end_year=year - 1,
            end_month=month,
        )
        budget = self.budget_service.get_overview(year=year, month=month)
        receivables = sum(
            (item.total for item in self.receivable_service.list_open_summary()),
            start=Decimal("0.00"),
        )
        intelligence = self.intelligence_service.get_overview(
            year=year,
            month=month,
        )
        recent = self.expense_management_service.list(
            limit=5,
            offset=0,
            month=month,
            year=year,
        )
        expenses = self.report_repository.list_for_period(
            start_year=year,
            start_month=month,
            end_year=year,
            end_month=month,
        )

        return DashboardOverview(
            year=year,
            month=month,
            spent=self._money(current.total_spent),
            planned_income=budget.monthly_income,
            reserve_target=budget.reserve_target,
            budget_remaining=budget.remaining,
            budget_status=budget.status,
            receivables=self._money(receivables),
            forecast_total=self._money(intelligence.summary.forecast_total),
            comparison=DashboardComparison(
                previous_month_total=self._money(previous.total_spent),
                previous_month_change_percent=self._change(
                    current.total_spent,
                    previous.total_spent,
                ),
                year_ago_total=self._money(year_ago.total_spent),
                year_ago_change_percent=self._change(
                    current.total_spent,
                    year_ago.total_spent,
                ),
            ),
            categories=current.categories,
            daily=self._daily_points(
                expenses=expenses,
                year=year,
                month=month,
            ),
            recent_expenses=recent.items,
        )

    def _daily_points(
        self,
        *,
        expenses: list[Expense],
        year: int,
        month: int,
    ) -> list[DashboardDailyPoint]:
        totals: dict[int, Decimal] = {}

        for expense in expenses:
            purchase_total = Decimal(str(expense.purchase_value))
            shared_total = sum(
                (Decimal(str(item.shared_value)) for item in expense.people),
                start=Decimal("0.00"),
            )
            owner_total = max(
                purchase_total - shared_total,
                Decimal("0.00"),
            )

            if expense.is_installment and purchase_total > 0:
                ratio = owner_total / purchase_total
                for installment in expense.installments:
                    due = installment.due_date
                    if (due.year, due.month) != (year, month):
                        continue
                    amount = Decimal(
                        str(installment.installment_value)
                    ) * ratio
                    totals[due.day] = totals.get(
                        due.day,
                        Decimal("0.00"),
                    ) + amount
                continue

            purchase_date = expense.purchase_date
            if (purchase_date.year, purchase_date.month) == (year, month):
                totals[purchase_date.day] = totals.get(
                    purchase_date.day,
                    Decimal("0.00"),
                ) + owner_total

        return [
            DashboardDailyPoint(day=day, total=self._money(total))
            for day, total in sorted(totals.items())
        ]

    @classmethod
    def _change(cls, current, previous) -> Decimal | None:
        current_value = Decimal(str(current))
        previous_value = Decimal(str(previous))
        if previous_value <= 0:
            return None
        return (
            (current_value - previous_value)
            / previous_value
            * cls.HUNDRED
        ).quantize(cls.CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
        absolute = year * 12 + month - 1 + offset
        return absolute // 12, absolute % 12 + 1

    @classmethod
    def _money(cls, value) -> Decimal:
        return Decimal(str(value)).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )
