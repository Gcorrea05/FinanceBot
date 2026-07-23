import re
from dataclasses import dataclass
from decimal import Decimal

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.money import MoneyParser
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)
from app.utils.text_normalizer import TextNormalizer


@dataclass(frozen=True)
class SharedAllocation:
    person_name: str
    normalized_name: str
    amount: Decimal


@dataclass(frozen=True)
class SharedSplitResult:
    owner_amount: Decimal
    allocations: tuple[SharedAllocation, ...]


class SharedExpenseSplitter:
    CENT = Decimal("0.01")
    MAX_NAME_LENGTH = 120
    _WHITESPACE = re.compile(r"\s+")

    def split(
        self,
        total: Decimal,
        people: tuple[SharedPersonCreate, ...],
    ) -> SharedSplitResult:
        validated_people = self._validate_people(
            people
        )

        amounts_provided = [
            person.amount is not None
            for person in validated_people
        ]

        if all(amounts_provided):
            return self._split_exact(
                total=total,
                people=validated_people,
            )

        if any(amounts_provided):
            raise ExpenseValidationError(
                "shared_people",
                (
                    "Informe o valor de todas as pessoas "
                    "ou deixe todos os valores vazios "
                    "para divisao igual."
                ),
            )

        return self._split_equal(
            total=total,
            people=validated_people,
        )

    def _validate_people(
        self,
        people: tuple[SharedPersonCreate, ...],
    ) -> tuple[SharedPersonCreate, ...]:
        if not people:
            raise ExpenseValidationError(
                "shared_people",
                (
                    "Uma despesa compartilhada deve "
                    "possuir pelo menos uma pessoa."
                ),
            )

        normalized_names: set[str] = set()
        validated: list[SharedPersonCreate] = []

        for person in people:
            if not isinstance(
                person,
                SharedPersonCreate,
            ):
                raise ExpenseValidationError(
                    "shared_people",
                    "Informe pessoas validas.",
                )

            name = self._WHITESPACE.sub(
                " ",
                person.name,
            ).strip()

            if len(name) < 2:
                raise ExpenseValidationError(
                    "shared_people",
                    (
                        "O nome da pessoa deve possuir "
                        "pelo menos 2 caracteres."
                    ),
                )

            if len(name) > self.MAX_NAME_LENGTH:
                raise ExpenseValidationError(
                    "shared_people",
                    (
                        "O nome da pessoa deve possuir "
                        f"no maximo {self.MAX_NAME_LENGTH} "
                        "caracteres."
                    ),
                )

            normalized_name = (
                TextNormalizer.normalize(name)
            )

            if normalized_name in normalized_names:
                raise ExpenseValidationError(
                    "shared_people",
                    (
                        f"A pessoa '{name}' foi informada "
                        "mais de uma vez."
                    ),
                )

            normalized_names.add(
                normalized_name
            )

            validated.append(
                SharedPersonCreate(
                    name=name,
                    amount=person.amount,
                )
            )

        return tuple(validated)

    def _split_equal(
        self,
        total: Decimal,
        people: tuple[SharedPersonCreate, ...],
    ) -> SharedSplitResult:
        participant_count = len(people) + 1

        amounts = self._split_amount(
            total=total,
            parts=participant_count,
        )

        owner_amount = amounts[0]

        allocations = tuple(
            SharedAllocation(
                person_name=person.name,
                normalized_name=(
                    TextNormalizer.normalize(
                        person.name
                    )
                ),
                amount=amounts[index + 1],
            )
            for index, person in enumerate(people)
        )

        return SharedSplitResult(
            owner_amount=owner_amount,
            allocations=allocations,
        )

    def _split_exact(
        self,
        total: Decimal,
        people: tuple[SharedPersonCreate, ...],
    ) -> SharedSplitResult:
        allocations: list[SharedAllocation] = []

        for person in people:
            try:
                amount = MoneyParser.parse(
                    person.amount
                )
            except ValueError as error:
                raise ExpenseValidationError(
                    "shared_people",
                    (
                        f"Valor invalido para "
                        f"'{person.name}': {error}"
                    ),
                ) from error

            allocations.append(
                SharedAllocation(
                    person_name=person.name,
                    normalized_name=(
                        TextNormalizer.normalize(
                            person.name
                        )
                    ),
                    amount=amount,
                )
            )

        allocated_total = sum(
            (
                allocation.amount
                for allocation in allocations
            ),
            start=Decimal("0.00"),
        )

        if allocated_total > total:
            raise ExpenseValidationError(
                "shared_people",
                (
                    "A soma das partes das pessoas "
                    "nao pode superar o valor da despesa."
                ),
            )

        return SharedSplitResult(
            owner_amount=(
                total - allocated_total
            ).quantize(self.CENT),
            allocations=tuple(allocations),
        )

    @classmethod
    def _split_amount(
        cls,
        total: Decimal,
        parts: int,
    ) -> tuple[Decimal, ...]:
        total_cents = int(
            (
                total.quantize(cls.CENT)
                * 100
            )
        )

        base_cents, remainder = divmod(
            total_cents,
            parts,
        )

        return tuple(
            Decimal(
                base_cents
                + (1 if index < remainder else 0)
            )
            / Decimal("100")
            for index in range(parts)
        )
