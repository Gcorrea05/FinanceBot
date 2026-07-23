import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.exceptions import (
    ExpenseValidationError,
)
from app.domain.money import MoneyParser
from app.schemas.expense.create import ExpenseCreate


@dataclass(frozen=True)
class ValidatedExpense:
    purchase_date: datetime
    purchase_place: str
    purchase_value: Decimal
    category: str
    payment_method: str
    is_installment: bool
    installments: int
    is_shared: bool
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

        is_shared = self._strict_bool(
            field="is_shared",
            value=data.is_shared,
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
            is_shared=is_shared,
            notes=notes,
        )

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
                "A quantidade de parcelas deve ser inteira.",
            )

        if not is_installment:
            if installments != 1:
                raise ExpenseValidationError(
                    "installments",
                    (
                        "Uma despesa nao parcelada "
                        "deve possuir exatamente 1 parcela."
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
    def _normalize_whitespace(
        cls,
        value: str,
    ) -> str:
        return cls._WHITESPACE.sub(
            " ",
            value,
        ).strip()
