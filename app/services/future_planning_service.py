from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.domain.billing_cycle import add_months
from app.repositories.recurring_expense_repository import RecurringExpenseRepository
from app.services.budget_service import BudgetService


@dataclass(frozen=True)
class FutureMonth:
    year: int
    month: int
    recorded_total: Decimal
    installment_total: Decimal
    recurring_total: Decimal
    committed_total: Decimal
    monthly_income: Decimal | None
    reserve_target: Decimal | None
    spending_limit: Decimal | None
    available_to_spend: Decimal | None
    status: str


class FuturePlanningService:
    CENT = Decimal("0.01")

    def __init__(
        self,
        *,
        budget_service: BudgetService,
        recurring_repository: RecurringExpenseRepository,
    ):
        self.budget_service = budget_service
        self.recurring_repository = recurring_repository

    def overview(
        self, *, from_year: int, from_month: int, months: int = 12
    ) -> list[FutureMonth]:
        if not 1 <= months <= 36:
            raise ValueError("O periodo deve possuir entre 1 e 36 meses.")
        result: list[FutureMonth] = []
        for offset in range(months):
            year, month = add_months(from_year, from_month, offset)
            expenses = self.budget_service.expense_repository.list_for_period(
                year=year, month=month
            )
            occurrences = self.recurring_repository.list_for_period(year, month)
            recurring_expense_ids = {
                item.expense_id
                for item in occurrences
                if item.status == "posted" and item.expense_id is not None
            }
            recorded = Decimal("0.00")
            installments = Decimal("0.00")
            recurring = Decimal("0.00")
            for expense in expenses:
                amount = self.budget_service._expense_amount(
                    expense=expense, year=year, month=month
                )
                if expense.id in recurring_expense_ids:
                    recurring += amount
                elif expense.is_installment:
                    installments += amount
                else:
                    recorded += amount
            recurring += sum(
                (
                    Decimal(str(item.amount)).quantize(self.CENT)
                    for item in occurrences
                    if item.status == "planned"
                ),
                Decimal("0.00"),
            )
            committed = (recorded + installments + recurring).quantize(self.CENT)
            budget = self.budget_service.get_overview(
                year=year, month=month, today=date(year, month, 1)
            )
            available = None
            if budget.spending_limit is not None:
                available = (budget.spending_limit - committed).quantize(
                    self.CENT, rounding=ROUND_HALF_UP
                )
            status = "not_configured"
            if available is not None:
                status = "exceeded" if available < 0 else "healthy"
                if budget.spending_limit and committed >= budget.spending_limit * Decimal("0.80"):
                    status = "attention" if available >= 0 else "exceeded"
            result.append(
                FutureMonth(
                    year=year,
                    month=month,
                    recorded_total=recorded.quantize(self.CENT),
                    installment_total=installments.quantize(self.CENT),
                    recurring_total=recurring.quantize(self.CENT),
                    committed_total=committed,
                    monthly_income=budget.monthly_income,
                    reserve_target=budget.reserve_target,
                    spending_limit=budget.spending_limit,
                    available_to_spend=available,
                    status=status,
                )
            )
        return result
