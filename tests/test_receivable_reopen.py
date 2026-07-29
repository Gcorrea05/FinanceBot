from datetime import datetime
from types import SimpleNamespace

from app.services.receivable_service import ReceivableService


class ReceivableRepositoryStub:
    def reopen(self, receivable_id):
        return SimpleNamespace(
            id=receivable_id,
            is_settled=False,
            settled_at=None,
        )

    def list_recent_settled(self, *, limit):
        return [
            SimpleNamespace(
                receivable_id=1,
                expense_id=2,
                person_id=3,
                person_name="Tomas",
                purchase_place="Mercado",
                purchase_date=datetime(2026, 7, 10),
                amount="25.00",
                settled_at=datetime(2026, 7, 20),
            )
        ]


class PersonRepositoryStub:
    pass


def test_reopens_settled_receivable():
    service = ReceivableService(
        receivable_repository=ReceivableRepositoryStub(),
        person_repository=PersonRepositoryStub(),
    )

    result = service.reopen(10)

    assert result.id == 10
    assert result.is_settled is False
    assert result.settled_at is None


def test_lists_recent_settled_receivables():
    service = ReceivableService(
        receivable_repository=ReceivableRepositoryStub(),
        person_repository=PersonRepositoryStub(),
    )

    rows = service.list_recent_settled(limit=5)

    assert rows[0].person_name == "Tomas"
    assert str(rows[0].amount) == "25.00"
