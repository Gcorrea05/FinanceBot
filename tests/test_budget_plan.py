from decimal import Decimal

import pytest

from app.domain.budget_plan import (
    BudgetPlanValidator,
    BudgetValidationError,
)


def test_validate_budget_plan():
    result = BudgetPlanValidator().validate(
        year=2026,
        month=7,
        monthly_income="5000,00",
        reserve_target="1000,00",
        spending_limit="3500,00",
    )

    assert result.monthly_income == Decimal(
        "5000.00"
    )
    assert result.reserve_target == Decimal(
        "1000.00"
    )
    assert result.spending_limit == Decimal(
        "3500.00"
    )


def test_reject_plan_above_income():
    with pytest.raises(
        BudgetValidationError,
        match="nao pode ultrapassar",
    ):
        BudgetPlanValidator().validate(
            year=2026,
            month=7,
            monthly_income="5000.00",
            reserve_target="1000.00",
            spending_limit="4500.00",
        )
