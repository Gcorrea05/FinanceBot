from datetime import date
from decimal import Decimal

import pytest

from app.bot.expense_input import (
    ExpenseInputError,
    format_brl,
    parse_date_input,
    parse_equal_people,
    parse_exact_people,
    parse_installment_count,
    parse_shared_mode,
    parse_yes_no,
)


def test_parse_today():
    assert parse_date_input(
        "Hoje",
        today=date(2026, 7, 23),
    ) == date(2026, 7, 23)


def test_parse_purchase_date_alias():
    assert parse_date_input(
        "Data da compra",
        purchase_date=date(2026, 7, 20),
    ) == date(2026, 7, 20)


def test_parse_explicit_date():
    assert parse_date_input(
        "05/08/2026"
    ) == date(2026, 8, 5)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("Sim", True),
        ("s", True),
        ("Nao", False),
        ("n\u00e3o", False),
    ],
)
def test_parse_yes_no(
    raw_value,
    expected,
):
    assert parse_yes_no(raw_value) is expected


def test_parse_installment_count():
    assert parse_installment_count("12") == 12


@pytest.mark.parametrize(
    "raw_value",
    [
        "1",
        "121",
        "abc",
    ],
)
def test_reject_invalid_installment_count(
    raw_value,
):
    with pytest.raises(ExpenseInputError):
        parse_installment_count(raw_value)


def test_parse_shared_mode():
    assert (
        parse_shared_mode("Divisao igual")
        == "equal"
    )

    assert (
        parse_shared_mode("Valores exatos")
        == "exact"
    )


def test_parse_equal_people():
    people = parse_equal_people(
        "Ana, Bruno"
    )

    assert [person.name for person in people] == [
        "Ana",
        "Bruno",
    ]

    assert all(
        person.amount is None
        for person in people
    )


def test_parse_exact_people():
    people = parse_exact_people(
        "Ana=30,00; Bruno=20,50"
    )

    assert people[0].name == "Ana"
    assert people[0].amount == Decimal("30.00")
    assert people[1].amount == Decimal("20.50")


def test_format_brl():
    assert (
        format_brl(Decimal("1234.56"))
        == "R$ 1.234,56"
    )
