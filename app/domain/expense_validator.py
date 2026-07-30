import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.money import MoneyParser
from app.schemas.expense.create import ExpenseCreate
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)


@dataclass(frozen=True)
class ValidatedExpense:
    purchase_date: datetime
    purchase_place: str
    purchase_value: Decimal
    category: str
    payment_method: str
    is_installment: bool
    installments: int
    first_installment_due_date: date | None
    is_shared: bool
    shared_people: tuple[SharedPersonCreate, ...]
    owner_amount: Decimal | None
    notes: str | None


class ExpenseValidator:
    """Centralizes expense business rules."""

    MAX_INSTALLMENTS = 120

    _WHITESPACE = re.compile(r"\s+")

    def validate(
        self,
        data: ExpenseCreate,
    ) -> ValidatedExpense:
        if not isinstance(data, ExpenseCreate):
            raise ExpenseValidationError(
                "expense",
                "Os dados informados sao invalidos.",
            )

        purchase_date = self._validate_date(
            data.purchase_date
        )

        purchase_place = self._required_text(
            field="purchase_place",
            value=data.purchase_place,
            minimum=2,
            maximum=255,
        )

        purchase_value = self._validate_money(
            data.purchase_value
        )

        category = self._required_text(
            field="category",
            value=data.category,
            minimum=2,
            maximum=100,
        )

        payment_method = self._required_text(
            field="payment_method",
            value=data.payment_method,
            minimum=2,
            maximum=100,
        )

        is_installment = self._strict_bool(
            field="is_installment",
            value=data.is_installment,
        )

        installments = self._validate_installments(
            is_installment=is_installment,
            installments=data.installments,
        )

        first_due_date = (
            self._validate_first_due_date(
                is_installment=is_installment,
                purchase_date=purchase_date,
                value=(
                    data.first_installment_due_date
                ),
            )
        )

        is_shared = self._strict_bool(
            field="is_shared",
            value=data.is_shared,
        )

        shared_people = self._validate_shared_people(
            is_shared=is_shared,
            value=data.shared_people,
        )

        owner_amount = self._validate_owner_amount(
            is_shared=is_shared, value=data.owner_amount
        )

        notes = self._optional_text(
            field="notes",
            value=data.notes,
            maximum=500,
        )

        return ValidatedExpense(
            purchase_date=purchase_date,
            purchase_place=purchase_place,
            purchase_value=purchase_value,
            category=category,
            payment_method=payment_method,
            is_installment=is_installment,
            installments=installments,
            first_installment_due_date=(
                first_due_date
            ),
            is_shared=is_shared,
            shared_people=shared_people,
            owner_amount=owner_amount,
            notes=notes,
        )


    @staticmethod
    def _validate_owner_amount(*, is_shared: bool, value) -> Decimal | None:
        if value is None:
            return None
        if not is_shared:
            raise ExpenseValidationError(
                "owner_amount",
                "Minha parte so pode ser informada em uma despesa compartilhada.",
            )
        try:
            return MoneyParser.parse(value)
        except ValueError as error:
            raise ExpenseValidationError("owner_amount", str(error)) from error

    @staticmethod
    def _validate_date(
        value: object,
    ) -> datetime:
        if not isinstance(value, datetime):
            raise ExpenseValidationError(
                "purchase_date",
                "Informe uma data e hora validas.",
            )

        return value

    @staticmethod
    def _validate_money(
        value: object,
    ) -> Decimal:
        try:
            return MoneyParser.parse(value)

        except ValueError as error:
            raise ExpenseValidationError(
                "purchase_value",
                str(error),
            ) from error

    @staticmethod
    def _validate_first_due_date(
        is_installment: bool,
        purchase_date: datetime,
        value: object,
    ) -> date | None:
        if not is_installment:
            if value is not None:
                raise ExpenseValidationError(
                    "first_installment_due_date",
                    (
                        "Uma despesa nao parcelada "
                        "nao deve possuir vencimento "
                        "de parcela."
                    ),
                )

            return None

        if value is None:
            return purchase_date.date()

        if isinstance(value, datetime):
            resolved_date = value.date()
        elif isinstance(value, date):
            resolved_date = value
        else:
            raise ExpenseValidationError(
                "first_installment_due_date",
                "Informe uma data valida.",
            )

        if resolved_date < purchase_date.date():
            raise ExpenseValidationError(
                "first_installment_due_date",
                (
                    "O primeiro vencimento nao pode "
                    "ser anterior a data da compra."
                ),
            )

        return resolved_date

    @staticmethod
    def _validate_shared_people(
        is_shared: bool,
        value: object,
    ) -> tuple[SharedPersonCreate, ...]:
        if value is None:
            people: tuple[SharedPersonCreate, ...] = ()
        elif isinstance(value, tuple):
            people = value
        elif isinstance(value, list):
            people = tuple(value)
        else:
            raise ExpenseValidationError(
                "shared_people",
                "Informe uma lista valida de pessoas.",
            )

        if is_shared and not people:
            raise ExpenseValidationError(
                "shared_people",
                (
                    "Uma despesa compartilhada deve "
                    "possuir pelo menos uma pessoa."
                ),
            )

        if not is_shared and people:
            raise ExpenseValidationError(
                "shared_people",
                (
                    "Uma despesa nao compartilhada "
                    "nao deve possuir pessoas."
                ),
            )

        return people

    @staticmethod
    def _strict_bool(
        field: str,
        value: object,
    ) -> bool:
        if type(value) is not bool:
            raise ExpenseValidationError(
                field,
                "Informe verdadeiro ou falso.",
            )

        return value

    @classmethod
    def _validate_installments(
        cls,
        is_installment: bool,
        installments: object,
    ) -> int:
        if (
            isinstance(installments, bool)
            or not isinstance(installments, int)
        ):
            raise ExpenseValidationError(
                "installments",
                (
                    "A quantidade de parcelas "
                    "deve ser inteira."
                ),
            )

        if not is_installment:
            if installments != 1:
                raise ExpenseValidationError(
                    "installments",
                    (
                        "Uma despesa nao parcelada "
                        "deve possuir exatamente "
                        "1 parcela."
                    ),
                )

            return 1

        if installments < 2:
            raise ExpenseValidationError(
                "installments",
                (
                    "Uma despesa parcelada deve possuir "
                    "pelo menos 2 parcelas."
                ),
            )

        if installments > cls.MAX_INSTALLMENTS:
            raise ExpenseValidationError(
                "installments",
                (
                    "A quantidade maxima permitida e "
                    f"{cls.MAX_INSTALLMENTS} parcelas."
                ),
            )

        return installments

    @classmethod
    def _required_text(
        cls,
        field: str,
        value: object,
        minimum: int,
        maximum: int,
    ) -> str:
        if not isinstance(value, str):
            raise ExpenseValidationError(
                field,
                "Informe um texto valido.",
            )

        normalized = cls._normalize_whitespace(
            value
        )

        if len(normalized) < minimum:
            raise ExpenseValidationError(
                field,
                (
                    "O texto deve possuir pelo menos "
                    f"{minimum} caracteres."
                ),
            )

        if len(normalized) > maximum:
            raise ExpenseValidationError(
                field,
                (
                    "O texto deve possuir no maximo "
                    f"{maximum} caracteres."
                ),
            )

        return normalized

    @classmethod
    def _optional_text(
        cls,
        field: str,
        value: object,
        maximum: int,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ExpenseValidationError(
                field,
                "Informe um texto valido.",
            )

        normalized = cls._normalize_whitespace(
            value
        )

        if not normalized:
            return None

        if len(normalized) > maximum:
            raise ExpenseValidationError(
                field,
                (
                    "O texto deve possuir no maximo "
                    f"{maximum} caracteres."
                ),
            )

        return normalized

    @classmethod
    def _normalize_whitespace(
        cls,
        value: str,
    ) -> str:
        return cls._WHITESPACE.sub(
            " ",
            value,
        ).strip()
