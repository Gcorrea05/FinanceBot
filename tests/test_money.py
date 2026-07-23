from decimal import Decimal

import pytest

from app.domain.money import MoneyParser


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("150,75", Decimal("150.75")),
        ("R$ 1.234,56", Decimal("1234.56")),
        ("1234.56", Decimal("1234.56")),
        (100, Decimal("100.00")),
        (10.999, Decimal("11.00")),
    ],
)
def test_parse_money(
    raw_value,
    expected,
):
    assert MoneyParser.parse(raw_value) == expected


@pytest.mark.parametrize(
    "raw_value",
    [
        "",
        "valor invalido",
        0,
        -10,
        True,
    ],
)
def test_reject_invalid_money(raw_value):
    with pytest.raises(ValueError):
        MoneyParser.parse(raw_value)
