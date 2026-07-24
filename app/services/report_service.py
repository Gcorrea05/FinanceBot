from dataclasses import dataclass
from datetime import date
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from app.database.models import Expense
from app.repositories.report_repository import (
    ReportRepository,
)


@dataclass(frozen=True)
class ReportPeriod:
    start_year: int
    start_month: int
    end_year: int
    end_month: int


@dataclass(frozen=True)
class MonthlyReportPoint:
    year: int
    month: int
    label: str
    total: Decimal


@dataclass(frozen=True)
class CategoryReportItem:
    name: str
    total: Decimal
    percentage: Decimal


@dataclass(frozen=True)
class MerchantReportItem:
    name: str
    total: Decimal
    transactions: int


@dataclass(frozen=True)
class InstallmentReportItem:
    expense_id: int
    purchase_place: str
    category: str
    payment_method: str
    purchase_value: Decimal
    owner_total: Decimal
    total_installments: int
    paid_installments: int
    pending_installments: int
    next_due_date: date | None
    remaining_amount: Decimal


@dataclass(frozen=True)
class ReportOverview:
    period: ReportPeriod
    total_spent: Decimal
    monthly_average: Decimal
    transactions: int
    highest_month: MonthlyReportPoint | None
    installment_commitment: Decimal
    monthly: list[MonthlyReportPoint]
    categories: list[CategoryReportItem]
    merchants: list[MerchantReportItem]
    installments: list[InstallmentReportItem]


class ReportService:
    CENT = Decimal("0.01")
    HUNDRED = Decimal("100.00")
    MAX_MONTHS = 24

    MONTH_LABELS = (
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    )

    def __init__(
        self,
        repository: ReportRepository,
    ):
        self.repository = repository

    def get_overview(
        self,
        *,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        category: str | None = None,
        payment_method: str | None = None,
        place: str | None = None,
    ) -> ReportOverview:
        month_keys = self._month_keys(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        expenses = self.repository.list_for_period(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
            category=category,
            payment_method=payment_method,
            place=place,
        )

        monthly_totals = {
            key: Decimal("0.00")
            for key in month_keys
        }
        category_totals: dict[
            str,
            Decimal,
        ] = {}
        merchant_totals: dict[
            str,
            Decimal,
        ] = {}
        merchant_transactions: dict[
            str,
            int,
        ] = {}

        transaction_count = 0
        installment_items: list[
            InstallmentReportItem
        ] = []

        for expense in expenses:
            contributions = (
                self._monthly_contributions(
                    expense=expense,
                    month_keys=set(
                        month_keys
                    ),
                )
            )

            relevant_total = sum(
                contributions.values(),
                start=Decimal("0.00"),
            ).quantize(
                self.CENT,
                rounding=ROUND_HALF_UP,
            )

            if relevant_total <= 0:
                continue

            transaction_count += 1

            for key, amount in (
                contributions.items()
            ):
                monthly_totals[key] += amount

            category_name = (
                expense.category.name
            )
            category_totals[
                category_name
            ] = (
                category_totals.get(
                    category_name,
                    Decimal("0.00"),
                )
                + relevant_total
            )

            merchant_name = (
                expense.purchase_place
            )
            merchant_totals[
                merchant_name
            ] = (
                merchant_totals.get(
                    merchant_name,
                    Decimal("0.00"),
                )
                + relevant_total
            )
            merchant_transactions[
                merchant_name
            ] = (
                merchant_transactions.get(
                    merchant_name,
                    0,
                )
                + 1
            )

            installment_item = (
                self._installment_item(
                    expense
                )
            )

            if installment_item is not None:
                installment_items.append(
                    installment_item
                )

        monthly = [
            MonthlyReportPoint(
                year=year,
                month=month,
                label=(
                    f"{self.MONTH_LABELS[month - 1]}"
                    f"/{str(year)[-2:]}"
                ),
                total=self._money(
                    monthly_totals[
                        (year, month)
                    ]
                ),
            )
            for year, month in month_keys
        ]

        total_spent = self._money(
            sum(
                (
                    item.total
                    for item in monthly
                ),
                start=Decimal("0.00"),
            )
        )

        monthly_average = self._money(
            total_spent
            / Decimal(
                len(monthly)
            )
        )

        highest_month = (
            max(
                monthly,
                key=lambda item: (
                    item.total,
                    -item.year,
                    -item.month,
                ),
            )
            if monthly
            else None
        )

        categories = self._categories(
            totals=category_totals,
            total_spent=total_spent,
        )

        merchants = [
            MerchantReportItem(
                name=name,
                total=self._money(total),
                transactions=(
                    merchant_transactions[
                        name
                    ]
                ),
            )
            for name, total in sorted(
                merchant_totals.items(),
                key=lambda item: (
                    -item[1],
                    item[0].lower(),
                ),
            )[:10]
        ]

        installment_items.sort(
            key=lambda item: (
                item.next_due_date
                or date.max,
                item.purchase_place.lower(),
            )
        )

        installment_commitment = (
            self._money(
                sum(
                    (
                        item.remaining_amount
                        for item in installment_items
                    ),
                    start=Decimal("0.00"),
                )
            )
        )

        return ReportOverview(
            period=ReportPeriod(
                start_year=start_year,
                start_month=start_month,
                end_year=end_year,
                end_month=end_month,
            ),
            total_spent=total_spent,
            monthly_average=monthly_average,
            transactions=transaction_count,
            highest_month=highest_month,
            installment_commitment=(
                installment_commitment
            ),
            monthly=monthly,
            categories=categories,
            merchants=merchants,
            installments=installment_items,
        )

    def _monthly_contributions(
        self,
        *,
        expense: Expense,
        month_keys: set[
            tuple[int, int]
        ],
    ) -> dict[
        tuple[int, int],
        Decimal,
    ]:
        purchase_total = self._money(
            expense.purchase_value
        )
        owner_total = self._owner_total(
            expense
        )

        if not expense.is_installment:
            key = (
                expense.purchase_date.year,
                expense.purchase_date.month,
            )

            if key not in month_keys:
                return {}

            return {
                key: owner_total
            }

        if purchase_total <= 0:
            return {}

        owner_ratio = (
            owner_total
            / purchase_total
        )

        contributions: dict[
            tuple[int, int],
            Decimal,
        ] = {}

        for installment in (
            expense.installments
        ):
            key = (
                installment.due_date.year,
                installment.due_date.month,
            )

            if key not in month_keys:
                continue

            amount = self._money(
                self._money(
                    installment.installment_value
                )
                * owner_ratio
            )

            contributions[key] = (
                contributions.get(
                    key,
                    Decimal("0.00"),
                )
                + amount
            )

        return contributions

    def _installment_item(
        self,
        expense: Expense,
    ) -> InstallmentReportItem | None:
        if not expense.is_installment:
            return None

        purchase_total = self._money(
            expense.purchase_value
        )

        if purchase_total <= 0:
            return None

        owner_total = self._owner_total(
            expense
        )
        owner_ratio = (
            owner_total
            / purchase_total
        )

        pending = [
            installment
            for installment in (
                expense.installments
            )
            if not installment.is_paid
        ]

        if not pending:
            return None

        paid_count = sum(
            1
            for installment in (
                expense.installments
            )
            if installment.is_paid
        )

        total_installments = max(
            (
                installment.total_installments
                for installment in (
                    expense.installments
                )
            ),
            default=len(
                expense.installments
            ),
        )

        remaining_amount = self._money(
            sum(
                (
                    self._money(
                        installment.installment_value
                    )
                    * owner_ratio
                    for installment in pending
                ),
                start=Decimal("0.00"),
            )
        )

        return InstallmentReportItem(
            expense_id=expense.id,
            purchase_place=(
                expense.purchase_place
            ),
            category=expense.category.name,
            payment_method=(
                expense.payment_method.name
            ),
            purchase_value=purchase_total,
            owner_total=owner_total,
            total_installments=(
                total_installments
            ),
            paid_installments=paid_count,
            pending_installments=len(
                pending
            ),
            next_due_date=min(
                installment.due_date
                for installment in pending
            ),
            remaining_amount=(
                remaining_amount
            ),
        )

    def _owner_total(
        self,
        expense: Expense,
    ) -> Decimal:
        purchase_total = self._money(
            expense.purchase_value
        )

        shared_total = sum(
            (
                self._money(
                    relation.shared_value
                )
                for relation in (
                    expense.people
                )
            ),
            start=Decimal("0.00"),
        )

        return max(
            purchase_total - shared_total,
            Decimal("0.00"),
        )

    def _categories(
        self,
        *,
        totals: dict[
            str,
            Decimal,
        ],
        total_spent: Decimal,
    ) -> list[
        CategoryReportItem
    ]:
        items: list[
            CategoryReportItem
        ] = []

        for name, total in sorted(
            totals.items(),
            key=lambda item: (
                -item[1],
                item[0].lower(),
            ),
        ):
            money_total = self._money(
                total
            )

            percentage = (
                self._money(
                    money_total
                    / total_spent
                    * self.HUNDRED
                )
                if total_spent > 0
                else Decimal("0.00")
            )

            items.append(
                CategoryReportItem(
                    name=name,
                    total=money_total,
                    percentage=percentage,
                )
            )

        return items

    @classmethod
    def _month_keys(
        cls,
        *,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ) -> list[
        tuple[int, int]
    ]:
        cls._validate_year(
            start_year
        )
        cls._validate_year(
            end_year
        )
        cls._validate_month(
            start_month
        )
        cls._validate_month(
            end_month
        )

        start = (
            start_year,
            start_month,
        )
        end = (
            end_year,
            end_month,
        )

        if start > end:
            raise ValueError(
                "O periodo inicial nao pode ser posterior ao periodo final."
            )

        result: list[
            tuple[int, int]
        ] = []
        year = start_year
        month = start_month

        while (
            year,
            month,
        ) <= end:
            result.append(
                (
                    year,
                    month,
                )
            )

            if len(result) > cls.MAX_MONTHS:
                raise ValueError(
                    "O relatorio permite no maximo 24 meses por consulta."
                )

            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        return result

    @staticmethod
    def _validate_year(
        year: int,
    ) -> None:
        if year < 2000 or year > 2100:
            raise ValueError(
                "O ano deve estar entre 2000 e 2100."
            )

    @staticmethod
    def _validate_month(
        month: int,
    ) -> None:
        if month < 1 or month > 12:
            raise ValueError(
                "O mes deve estar entre 1 e 12."
            )

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:
        return Decimal(
            str(value)
        ).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )
