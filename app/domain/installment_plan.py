import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.domain.exceptions import (
    ExpenseValidationError,
)


@dataclass(frozen=True)
class InstallmentPlanItem:
    installment_number: int
    total_installments: int
    due_date: date
    amount: Decimal


class InstallmentPlanBuilder:
    CENT = Decimal("0.01")

    def build(
        self,
        total: Decimal,
        installments: int,
        first_due_date: date,
    ) -> tuple[InstallmentPlanItem, ...]:
        if installments < 2:
            raise ExpenseValidationError(
                "installments",
                (
                    "O plano parcelado deve possuir "
                    "pelo menos 2 parcelas."
                ),
            )

        amounts = self._split_amount(
            total=total,
            parts=installments,
        )

        return tuple(
            InstallmentPlanItem(
                installment_number=index + 1,
                total_installments=installments,
                due_date=self._add_months(
                    first_due_date,
                    index,
                ),
                amount=amount,
            )
            for index, amount in enumerate(amounts)
        )

    @classmethod
    def _split_amount(
        cls,
        total: Decimal,
        parts: int,
    ) -> tuple[Decimal, ...]:
        if total <= 0:
            raise ExpenseValidationError(
                "purchase_value",
                "O valor deve ser maior que zero.",
            )

        if parts <= 0:
            raise ExpenseValidationError(
                "installments",
                "A quantidade de parcelas deve ser positiva.",
            )

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

    @staticmethod
    def _add_months(
        original_date: date,
        months: int,
    ) -> date:
        month_index = (
            original_date.month - 1 + months
        )

        year = (
            original_date.year
            + month_index // 12
        )

        month = (
            month_index % 12
            + 1
        )

        last_day = calendar.monthrange(
            year,
            month,
        )[1]

        day = min(
            original_date.day,
            last_day,
        )

        return date(
            year,
            month,
            day,
        )
