from decimal import Decimal

import pytest

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.shared_expense import (
    SharedExpenseSplitter,
)
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)


def test_equal_split_includes_owner():
    result = SharedExpenseSplitter().split(
        total=Decimal("100.00"),
        people=(
            SharedPersonCreate(name="Ana"),
            SharedPersonCreate(name="Bruno"),
        ),
    )

    assert result.owner_amount == Decimal("33.34")

    assert [
        allocation.amount
        for allocation in result.allocations
    ] == [
        Decimal("33.33"),
        Decimal("33.33"),
    ]


def test_exact_split_keeps_owner_remainder():
    result = SharedExpenseSplitter().split(
        total=Decimal("100.00"),
        people=(
            SharedPersonCreate(
                name="Ana",
                amount="25,00",
            ),
            SharedPersonCreate(
                name="Bruno",
                amount="30,00",
            ),
        ),
    )

    assert result.owner_amount == Decimal("45.00")

    assert sum(
        (
            allocation.amount
            for allocation in result.allocations
        ),
        start=Decimal("0.00"),
    ) == Decimal("55.00")


def test_reject_mixed_split_modes():
    with pytest.raises(
        ExpenseValidationError,
        match="shared_people",
    ):
        SharedExpenseSplitter().split(
            total=Decimal("100.00"),
            people=(
                SharedPersonCreate(
                    name="Ana",
                    amount="25,00",
                ),
                SharedPersonCreate(
                    name="Bruno",
                ),
            ),
        )


def test_reject_duplicate_people():
    with pytest.raises(
        ExpenseValidationError,
        match="mais de uma vez",
    ):
        SharedExpenseSplitter().split(
            total=Decimal("100.00"),
            people=(
                SharedPersonCreate(
                    name="Ana",
                ),
                SharedPersonCreate(
                    name="\u00c1NA",
                ),
            ),
        )


def test_reject_exact_split_above_total():
    with pytest.raises(
        ExpenseValidationError,
        match="superar",
    ):
        SharedExpenseSplitter().split(
            total=Decimal("100.00"),
            people=(
                SharedPersonCreate(
                    name="Ana",
                    amount="60,00",
                ),
                SharedPersonCreate(
                    name="Bruno",
                    amount="50,00",
                ),
            ),
        )
