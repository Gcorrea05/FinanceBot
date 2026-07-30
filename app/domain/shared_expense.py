import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.domain.exceptions import ExpenseValidationError
from app.domain.money import MoneyParser
from app.schemas.expense.shared_person import SharedPersonCreate
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
        owner_amount=None,
    ) -> SharedSplitResult:
        validated = self._validate_people(people)
        explicit_owner = self._optional_money(owner_amount, "minha parte")

        parsed: list[tuple[SharedPersonCreate, Decimal | None]] = []
        explicit_total = explicit_owner or Decimal("0.00")
        unspecified = 0

        for person in validated:
            amount = self._optional_money(person.amount, person.name)
            parsed.append((person, amount))
            if amount is None:
                unspecified += 1
            else:
                explicit_total += amount

        if explicit_total > total:
            raise ExpenseValidationError(
                "shared_people",
                "A soma das partes informadas supera o valor total.",
            )

        owner_unspecified = explicit_owner is None
        slots = unspecified + (1 if owner_unspecified else 0)
        remainder = (total - explicit_total).quantize(self.CENT)

        if slots == 0 and remainder != Decimal("0.00"):
            raise ExpenseValidationError(
                "shared_people",
                "Os valores informados nao fecham o total da despesa.",
            )

        distributed = self._split_amount(remainder, slots) if slots else ()
        cursor = 0

        if owner_unspecified:
            owner = distributed[cursor]
            cursor += 1
        else:
            owner = explicit_owner

        allocations: list[SharedAllocation] = []
        for person, amount in parsed:
            resolved = amount
            if resolved is None:
                resolved = distributed[cursor]
                cursor += 1
            allocations.append(
                SharedAllocation(
                    person_name=person.name,
                    normalized_name=TextNormalizer.normalize(person.name),
                    amount=resolved.quantize(self.CENT),
                )
            )

        allocated = sum((item.amount for item in allocations), Decimal("0.00"))
        difference = (total - owner - allocated).quantize(self.CENT)
        if difference:
            # Centavos de arredondamento ficam com o proprietario sempre que
            # a parte dele nao foi explicitamente fixada.
            if owner_unspecified:
                owner = (owner + difference).quantize(self.CENT)
            elif allocations:
                last = allocations[-1]
                allocations[-1] = SharedAllocation(
                    last.person_name,
                    last.normalized_name,
                    (last.amount + difference).quantize(self.CENT),
                )
            else:
                raise ExpenseValidationError(
                    "shared_people", "Nao foi possivel fechar a divisao."
                )

        return SharedSplitResult(owner.quantize(self.CENT), tuple(allocations))

    def _validate_people(
        self, people: tuple[SharedPersonCreate, ...]
    ) -> tuple[SharedPersonCreate, ...]:
        if not people:
            raise ExpenseValidationError(
                "shared_people",
                "Uma despesa compartilhada deve possuir pelo menos uma pessoa.",
            )
        seen: set[str] = set()
        result: list[SharedPersonCreate] = []
        for person in people:
            if not isinstance(person, SharedPersonCreate):
                raise ExpenseValidationError("shared_people", "Informe pessoas validas.")
            name = self._WHITESPACE.sub(" ", person.name).strip()
            if len(name) < 2 or len(name) > self.MAX_NAME_LENGTH:
                raise ExpenseValidationError(
                    "shared_people", "O nome deve possuir entre 2 e 120 caracteres."
                )
            normalized = TextNormalizer.normalize(name)
            if normalized in seen:
                raise ExpenseValidationError(
                    "shared_people", f"A pessoa '{name}' foi informada mais de uma vez."
                )
            seen.add(normalized)
            result.append(SharedPersonCreate(name=name, amount=person.amount))
        return tuple(result)

    @staticmethod
    def _optional_money(value, label: str) -> Decimal | None:
        if value is None:
            return None
        try:
            return MoneyParser.parse(value)
        except ValueError as error:
            raise ExpenseValidationError(
                "shared_people", f"Valor invalido para '{label}': {error}"
            ) from error

    @classmethod
    def _split_amount(cls, total: Decimal, parts: int) -> tuple[Decimal, ...]:
        if parts <= 0:
            return ()
        cents = int((total.quantize(cls.CENT, rounding=ROUND_HALF_UP)) * 100)
        base, remainder = divmod(cents, parts)
        return tuple(
            (Decimal(base + (1 if index < remainder else 0)) / Decimal("100"))
            for index in range(parts)
        )
