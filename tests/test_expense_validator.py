from datetime import datetime
from decimal import Decimal

import pytest

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.expense_validator import (
    ExpenseValidator,
)
from app.schemas.expense.create import ExpenseCreate


def make_expense(
    **changes,
) -> ExpenseCreate:
    values = {
        "purchase_date": datetime(
            2026,
            7,
            23,
            10,
            30,
        ),
        "purchase_place": "Mercado Central",
        "purchase_value": "150,75",
        "category": "Mercado",
        "payment_method": "Pix",
        "is_installment": False,
        "installments": 1,
        "is_shared": False,
        "notes": None,
    }

    values.update(changes)

    return ExpenseCreate(**values)


def test_validate_and_normalize_expense():
    validator = ExpenseValidator()

    validated = validator.validate(
        make_expense(
            purchase_place=(
                "  Mercado   Central  "
            ),
            notes="  Compra   mensal  ",
        )
    )

    assert (
        validated.purchase_place
        == "Mercado Central"
    )

    assert (
        validated.purchase_value
        == Decimal("150.75")
    )

    assert validated.notes == "Compra mensal"


def test_empty_notes_become_none():
    validated = ExpenseValidator().validate(
        make_expense(notes="   ")
    )

    assert validated.notes is None


def test_reject_zero_value():
    with pytest.raises(
        ExpenseValidationError,
        match="purchase_value",
    ):
        ExpenseValidator().validate(
            make_expense(
                purchase_value=0
            )
        )


def test_reject_empty_place():
    with pytest.raises(
        ExpenseValidationError,
        match="purchase_place",
    ):
        ExpenseValidator().validate(
            make_expense(
                purchase_place=" "
            )
        )


def test_non_installment_requires_one_installment():
    with pytest.raises(
        ExpenseValidationError,
        match="installments",
    ):
        ExpenseValidator().validate(
            make_expense(
                is_installment=False,
                installments=2,
            )
        )


def test_installment_expense_requires_two_or_more():
    with pytest.raises(
        ExpenseValidationError,
        match="installments",
    ):
        ExpenseValidator().validate(
            make_expense(
                is_installment=True,
                installments=1,
            )
        )


def test_accept_valid_installment_expense():
    validated = ExpenseValidator().validate(
        make_expense(
            is_installment=True,
            installments=12,
        )
    )

    assert validated.is_installment is True
    assert validated.installments == 12


def test_reject_non_boolean_flags():
    with pytest.raises(
        ExpenseValidationError,
        match="is_shared",
    ):
        ExpenseValidator().validate(
            make_expense(
                is_shared=1
            )
        )
