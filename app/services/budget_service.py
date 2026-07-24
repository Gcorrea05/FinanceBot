import calendar
from dataclasses import dataclass
from datetime import date
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from app.database.models import (
    Budget,
    Expense,
)
from app.domain.budget_plan import (
    BudgetPlanValidator,
)
from app.repositories.budget_expense_repository import (
    BudgetExpenseRepository,
)
from app.repositories.budget_repository import (
    BudgetRepository,
)


@dataclass(frozen=True)
class BudgetOverview:
    year: int
    month: int
    configured: bool
    monthly_income: Decimal | None
    reserve_target: Decimal | None
    spending_limit: Decimal | None
    spent: Decimal
    remaining: Decimal | None
    available_after_reserve: Decimal | None
    daily_limit: Decimal | None
    usage_percent: Decimal | None
    remaining_days: int
    status: str


class BudgetService:
    CENT = Decimal("0.01")
    HUNDRED = Decimal("100.00")

    def __init__(
        self,
        budget_repository: BudgetRepository,
        expense_repository: BudgetExpenseRepository,
        validator: BudgetPlanValidator | None = None,
    ):
        self.budget_repository = budget_repository
        self.expense_repository = expense_repository
        self.validator = (
            validator
            if validator is not None
            else BudgetPlanValidator()
        )

    def save_plan(
        self,
        *,
        year: int,
        month: int,
        monthly_income,
        reserve_target,
        spending_limit,
    ) -> BudgetOverview:
        plan = self.validator.validate(
            year=year,
            month=month,
            monthly_income=monthly_income,
            reserve_target=reserve_target,
            spending_limit=spending_limit,
        )

        self.budget_repository.save_plan(
            year=plan.year,
            month=plan.month,
            monthly_income=plan.monthly_income,
            reserve_target=plan.reserve_target,
            spending_limit=plan.spending_limit,
        )

        return self.get_overview(
            year=plan.year,
            month=plan.month,
        )

    def get_overview(
        self,
        *,
        year: int,
        month: int,
        today: date | None = None,
    ) -> BudgetOverview:
        self.validator._year(year)
        self.validator._month(month)

        budget = self.budget_repository.get_by_period(
            year=year,
            month=month,
        )

        expenses = self.expense_repository.list_for_period(
            year=year,
            month=month,
        )

        spent = self._spent_for_period(
            expenses=expenses,
            year=year,
            month=month,
        )

        remaining_days = self._remaining_days(
            year=year,
            month=month,
            today=today or date.today(),
        )

        if budget is None:
            return BudgetOverview(
                year=year,
                month=month,
                configured=False,
                monthly_income=None,
                reserve_target=None,
                spending_limit=None,
                spent=spent,
                remaining=None,
                available_after_reserve=None,
                daily_limit=None,
                usage_percent=None,
                remaining_days=remaining_days,
                status="not_configured",
            )

        return self._configured_overview(
            budget=budget,
            spent=spent,
            remaining_days=remaining_days,
        )

    def _configured_overview(
        self,
        *,
        budget: Budget,
        spent: Decimal,
        remaining_days: int,
    ) -> BudgetOverview:
        income = self._money(
            budget.monthly_income
        )
        reserve = self._money(
            budget.reserve_target
        )
        limit = self._money(
            budget.spending_limit
        )

        remaining = (
            limit - spent
        ).quantize(self.CENT)

        available_after_reserve = (
            income - reserve - spent
        ).quantize(self.CENT)

        usage_percent = (
            (
                spent
                / limit
                * self.HUNDRED
            )
            if limit > 0
            else Decimal("0.00")
        ).quantize(self.CENT)

        positive_remaining = max(
            remaining,
            Decimal("0.00"),
        )

        daily_limit = (
            positive_remaining
            / remaining_days
            if remaining_days > 0
            else Decimal("0.00")
        ).quantize(
            self.CENT,
            rounding=ROUND_HALF_UP,
        )

        if spent > limit:
            status = "exceeded"
        elif usage_percent >= Decimal("80.00"):
            status = "attention"
        else:
            status = "healthy"

        return BudgetOverview(
            year=budget.year,
            month=budget.month,
            configured=True,
            monthly_income=income,
            reserve_target=reserve,
            spending_limit=limit,
            spent=spent,
            remaining=remaining,
            available_after_reserve=available_after_reserve,
            daily_limit=daily_limit,
            usage_percent=usage_percent,
            remaining_days=remaining_days,
            status=status,
        )

    def _spent_for_period(
        self,
        *,
        expenses: list[Expense],
        year: int,
        month: int,
    ) -> Decimal:
        total = sum(
            (
                self._expense_amount(
                    expense=expense,
                    year=year,
                    month=month,
                )
                for expense in expenses
            ),
            start=Decimal("0.00"),
        )

        return total.quantize(
            self.CENT,
            rounding=ROUND_HALF_UP,
        )

    def _expense_amount(
        self,
        *,
        expense: Expense,
        year: int,
        month: int,
    ) -> Decimal:
        purchase_total = self._money(
            expense.purchase_value
        )

        shared_total = sum(
            (
                self._money(
                    relation.shared_value
                )
                for relation in expense.people
            ),
            start=Decimal("0.00"),
        )

        owner_total = max(
            purchase_total - shared_total,
            Decimal("0.00"),
        )

        if not expense.is_installment:
            return owner_total

        if purchase_total <= 0:
            return Decimal("0.00")

        due_total = sum(
            (
                self._money(
                    installment.installment_value
                )
                for installment in expense.installments
                if (
                    installment.due_date.year == year
                    and installment.due_date.month == month
                )
            ),
            start=Decimal("0.00"),
        )

        owner_ratio = (
            owner_total
            / purchase_total
        )

        return (
            due_total
            * owner_ratio
        ).quantize(
            self.CENT,
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:
        return Decimal(
            str(value)
        ).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _remaining_days(
        *,
        year: int,
        month: int,
        today: date,
    ) -> int:
        target = (
            year,
            month,
        )

        current = (
            today.year,
            today.month,
        )

        days_in_month = calendar.monthrange(
            year,
            month,
        )[1]

        if target < current:
            return 0

        if target > current:
            return days_in_month

        return max(
            days_in_month - today.day + 1,
            0,
        )
