from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.receivable_service import (
    ReceivableNotFoundError,
    ReceivableService,
)


class PersonRepositoryStub:
    def __init__(self):
        self.person = SimpleNamespace(
            id=10,
            name="Tomas",
        )

    def get_by_normalized_name(
        self,
        normalized_name,
    ):
        if normalized_name == "tomas":
            return self.person

        return None


class ReceivableRepositoryStub:
    def __init__(self):
        self.settled_id = None

    def list_open_summary(self):
        return [
            SimpleNamespace(
                person_id=10,
                person_name="Tomas",
                total=Decimal("120.50"),
                pending_count=2,
            )
        ]

    def list_open_for_person(
        self,
        person_id,
    ):
        return [
            SimpleNamespace(
                receivable_id=1,
                expense_id=99,
                person_id=person_id,
                person_name="Tomas",
                purchase_place="Mercado",
                purchase_date=datetime(
                    2026,
                    7,
                    23,
                ),
                amount=Decimal("70.00"),
            )
        ]

    def settle(self, receivable_id):
        if receivable_id != 1:
            return None

        self.settled_id = receivable_id
        return SimpleNamespace(
            id=receivable_id
        )


def make_service():
    repository = ReceivableRepositoryStub()

    return (
        ReceivableService(
            receivable_repository=repository,
            person_repository=(
                PersonRepositoryStub()
            ),
        ),
        repository,
    )


def test_list_open_summary():
    service, _ = make_service()

    summary = service.list_open_summary()

    assert summary[0].person_name == "Tomas"
    assert summary[0].total == Decimal(
        "120.50"
    )
    assert summary[0].pending_count == 2


def test_list_open_for_person_name():
    service, _ = make_service()

    items = (
        service.list_open_for_person_name(
            "TOMAS"
        )
    )

    assert items[0].amount == Decimal(
        "70.00"
    )


def test_unknown_person_raises():
    service, _ = make_service()

    with pytest.raises(
        ReceivableNotFoundError,
    ):
        service.list_open_for_person_name(
            "Desconhecido"
        )


def test_settle_receivable():
    service, repository = make_service()

    service.settle(1)

    assert repository.settled_id == 1
