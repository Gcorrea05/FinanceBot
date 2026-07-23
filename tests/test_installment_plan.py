from datetime import date
from decimal import Decimal

import pytest

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.installment_plan import (
    InstallmentPlanBuilder,
)


def test_build_installments_preserves_total():
    plan = InstallmentPlanBuilder().build(
        total=Decimal("100.00"),
        installments=3,
        first_due_date=date(
            2026,
            1,
            31,
        ),
    )

    assert [
        item.amount
        for item in plan
    ] == [
        Decimal("33.34"),
        Decimal("33.33"),
        Decimal("33.33"),
    ]

    assert sum(
        (
            item.amount
            for item in plan
        ),
        start=Decimal("0.00"),
    ) == Decimal("100.00")


def test_build_installments_clamps_month_end():
    plan = InstallmentPlanBuilder().build(
        total=Decimal("300.00"),
        installments=3,
        first_due_date=date(
            2026,
            1,
            31,
        ),
    )

    assert [
        item.due_date
        for item in plan
    ] == [
        date(2026, 1, 31),
        date(2026, 2, 28),
        date(2026, 3, 31),
    ]


def test_reject_single_installment_plan():
    with pytest.raises(
        ExpenseValidationError,
        match="installments",
    ):
        InstallmentPlanBuilder().build(
            total=Decimal("100.00"),
            installments=1,
            first_due_date=date(
                2026,
                1,
                1,
            ),
        )
