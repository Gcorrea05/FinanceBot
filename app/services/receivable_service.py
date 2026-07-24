from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.repositories.person_repository import (
    PersonRepository,
)
from app.repositories.receivable_repository import (
    ReceivableRepository,
)
from app.utils.text_normalizer import TextNormalizer


class ReceivableNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class ReceivableSummary:
    person_id: int
    person_name: str
    total: Decimal
    pending_count: int


@dataclass(frozen=True)
class ReceivableItem:
    receivable_id: int
    expense_id: int
    person_id: int
    person_name: str
    purchase_place: str
    purchase_date: datetime
    amount: Decimal


class ReceivableService:
    CENT = Decimal("0.01")

    def __init__(
        self,
        receivable_repository: ReceivableRepository,
        person_repository: PersonRepository,
    ):
        self.receivable_repository = (
            receivable_repository
        )
        self.person_repository = person_repository

    def list_open_summary(
        self,
    ) -> list[ReceivableSummary]:
        return [
            ReceivableSummary(
                person_id=row.person_id,
                person_name=row.person_name,
                total=self._money(row.total),
                pending_count=int(
                    row.pending_count
                ),
            )
            for row
            in self.receivable_repository
            .list_open_summary()
        ]

    def list_open_for_person_name(
        self,
        person_name: str,
    ) -> list[ReceivableItem]:
        normalized_name = (
            TextNormalizer.normalize(
                person_name
            )
        )

        person = (
            self.person_repository
            .get_by_normalized_name(
                normalized_name
            )
        )

        if person is None:
            raise ReceivableNotFoundError(
                (
                    f"Pessoa '{person_name}' "
                    "nao encontrada."
                )
            )

        return self.list_open_for_person_id(
            person.id
        )

    def list_open_for_person_id(
        self,
        person_id: int,
    ) -> list[ReceivableItem]:
        return [
            ReceivableItem(
                receivable_id=(
                    row.receivable_id
                ),
                expense_id=row.expense_id,
                person_id=row.person_id,
                person_name=row.person_name,
                purchase_place=(
                    row.purchase_place
                ),
                purchase_date=(
                    row.purchase_date
                ),
                amount=self._money(
                    row.amount
                ),
            )
            for row
            in self.receivable_repository
            .list_open_for_person(
                person_id
            )
        ]

    def settle(
        self,
        receivable_id: int,
    ):
        receivable = (
            self.receivable_repository
            .settle(receivable_id)
        )

        if receivable is None:
            raise ReceivableNotFoundError(
                (
                    "A pendencia nao existe "
                    "ou ja foi recebida."
                )
            )

        return receivable

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:
        return Decimal(
            str(value)
        ).quantize(cls.CENT)
