from dataclasses import dataclass
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
)

from app.domain.exceptions import DomainError


class BudgetValidationError(DomainError):
    def __init__(
        self,
        field: str,
        message: str,
    ):
        self.field = field
        self.message = message

        super().__init__(
            f"{field}: {message}"
        )


@dataclass(frozen=True)
class ValidatedBudgetPlan:
    year: int
    month: int
    monthly_income: Decimal
    reserve_target: Decimal
    spending_limit: Decimal


class BudgetPlanValidator:
    CENT = Decimal("0.01")
    MAX_VALUE = Decimal("999999999.99")

    def validate(
        self,
        *,
        year: int,
        month: int,
        monthly_income,
        reserve_target,
        spending_limit,
    ) -> ValidatedBudgetPlan:
        validated_year = self._year(year)
        validated_month = self._month(month)

        income = self._money(
            "monthly_income",
            monthly_income,
            allow_zero=False,
        )

        reserve = self._money(
            "reserve_target",
            reserve_target,
            allow_zero=True,
        )

        limit = self._money(
            "spending_limit",
            spending_limit,
            allow_zero=False,
        )

        if reserve > income:
            raise BudgetValidationError(
                "reserve_target",
                (
                    "A reserva nao pode ser maior "
                    "que a renda mensal."
                ),
            )

        if limit + reserve > income:
            raise BudgetValidationError(
                "spending_limit",
                (
                    "O limite de gastos somado a reserva "
                    "nao pode ultrapassar a renda mensal."
                ),
            )

        return ValidatedBudgetPlan(
            year=validated_year,
            month=validated_month,
            monthly_income=income,
            reserve_target=reserve,
            spending_limit=limit,
        )

    @staticmethod
    def _year(value: int) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 2000 <= value <= 2100
        ):
            raise BudgetValidationError(
                "year",
                "Informe um ano entre 2000 e 2100.",
            )

        return value

    @staticmethod
    def _month(value: int) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 1 <= value <= 12
        ):
            raise BudgetValidationError(
                "month",
                "Informe um mes entre 1 e 12.",
            )

        return value

    @classmethod
    def _money(
        cls,
        field: str,
        value,
        *,
        allow_zero: bool,
    ) -> Decimal:
        if isinstance(value, bool):
            raise BudgetValidationError(
                field,
                "Informe um valor monetario valido.",
            )

        try:
            if isinstance(value, Decimal):
                amount = value
            elif isinstance(value, (int, float)):
                amount = Decimal(str(value))
            elif isinstance(value, str):
                normalized = (
                    value.strip()
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
                    normalized = normalized.replace(",", ".")

                amount = Decimal(normalized)
            else:
                raise TypeError
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise BudgetValidationError(
                field,
                "Informe um valor monetario valido.",
            ) from error

        if not amount.is_finite():
            raise BudgetValidationError(
                field,
                "O valor deve ser finito.",
            )

        minimum = Decimal("0.00") if allow_zero else cls.CENT

        if amount < minimum:
            message = (
                "O valor nao pode ser negativo."
                if allow_zero
                else "O valor deve ser maior que zero."
            )

            raise BudgetValidationError(
                field,
                message,
            )

        if amount > cls.MAX_VALUE:
            raise BudgetValidationError(
                field,
                "O valor excede o limite permitido.",
            )

        return amount.quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )
