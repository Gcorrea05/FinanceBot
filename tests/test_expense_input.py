from decimal import Decimal

from app.bot.expense_input import format_brl


def test_format_brl():
    assert (
        format_brl(Decimal("1234.56"))
        == "R$ 1.234,56"
    )