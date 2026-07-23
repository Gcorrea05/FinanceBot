from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
)
from typing import TypeAlias


MoneyInput: TypeAlias = (
    Decimal
    | int
    | float
    | str
)


class MoneyParser:
    """Converts monetary input into a validated Decimal."""

    CENT = Decimal("0.01")
    MAX_VALUE = Decimal("999999999.99")

    @classmethod
    def parse(
        cls,
        value: MoneyInput,
    ) -> Decimal:
        if isinstance(value, bool):
            raise ValueError(
                "O valor monetario nao pode ser booleano."
            )

        try:
            amount = cls._to_decimal(value)

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:
            raise ValueError(
                "Informe um valor monetario valido."
            ) from error

        if not amount.is_finite():
            raise ValueError(
                "O valor monetario deve ser finito."
            )

        if amount <= 0:
            raise ValueError(
                "O valor deve ser maior que zero."
            )

        if amount > cls.MAX_VALUE:
            raise ValueError(
                "O valor excede o limite permitido."
            )

        return amount.quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def _to_decimal(
        cls,
        value: MoneyInput,
    ) -> Decimal:
        if isinstance(value, Decimal):
            return value

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        if not isinstance(value, str):
            raise TypeError(
                "Tipo de valor monetario invalido."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Valor monetario vazio."
            )

        normalized = (
            normalized
            .replace("R$", "")
            .replace("r$", "")
            .replace(" ", "")
        )

        if "," in normalized and "." in normalized:
            if normalized.rfind(",") > normalized.rfind("."):
                normalized = (
                    normalized
                    .replace(".", "")
                    .replace(",", ".")
                )
            else:
                normalized = normalized.replace(",", "")

        elif "," in normalized:
            if normalized.count(",") != 1:
                raise ValueError(
                    "Formato monetario invalido."
                )

            normalized = normalized.replace(",", ".")

        elif normalized.count(".") > 1:
            raise ValueError(
                "Formato monetario invalido."
            )

        return Decimal(normalized)
