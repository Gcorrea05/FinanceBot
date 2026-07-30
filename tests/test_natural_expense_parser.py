from decimal import Decimal

import pytest

from app.domain.natural_expense_parser import NaturalExpenseParseError, NaturalExpenseParser


def test_parses_installment_message():
    draft = NaturalExpenseParser().parse("tablet 1700 parcelado em 10x")
    assert draft.description == "tablet"
    assert draft.total == Decimal("1700.00")
    assert draft.installments == 10
    assert draft.category == "Eletronicos"


def test_shared_message_always_keeps_owner_in_split():
    draft = NaturalExpenseParser().parse(
        "Presente Giron, 300, Tomas, Yuzo, Pasquale, Sofia, Vitor"
    )
    assert len(draft.shared_people) == 5
    assert draft.owner_amount is None


def test_parses_explicit_owner_amount():
    draft = NaturalExpenseParser().parse(
        "Presente, 300, Tomas, Yuzo, minha parte 100"
    )
    assert draft.owner_amount == Decimal("100.00")


def test_rejects_installment_and_recurring_in_same_message():
    with pytest.raises(NaturalExpenseParseError):
        NaturalExpenseParser().parse("tablet 1700 em 10x mensal dia 2")
