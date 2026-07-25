from __future__ import annotations

import calendar
import re
import statistics
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from app.database.models import Expense
from app.repositories.report_repository import ReportRepository
from app.services.budget_service import BudgetService
from app.services.report_service import MonthlyReportPoint, ReportService


@dataclass(frozen=True)
class IntelligenceSummary:
    current_total: Decimal
    forecast_total: Decimal
    historical_average: Decimal
    trend_percent: Decimal | None
    installment_commitment: Decimal
    budget_usage_percent: Decimal | None
    budget_status: str
    data_months: int


@dataclass(frozen=True)
class IntelligenceInsight:
    code: str
    kind: str
    severity: str
    title: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class IntelligenceAnomaly:
    expense_id: int
    purchase_date: date
    purchase_place: str
    category: str
    amount: Decimal
    category_median: Decimal
    difference_percent: Decimal


@dataclass(frozen=True)
class IntelligenceRecurringExpense:
    purchase_place: str
    category: str
    occurrences: int
    average_amount: Decimal
    last_purchase_date: date
    expected_next_date: date


@dataclass(frozen=True)
class IntelligenceOverview:
    year: int
    month: int
    generated_at: datetime
    summary: IntelligenceSummary
    monthly: list[MonthlyReportPoint]
    insights: list[IntelligenceInsight]
    anomalies: list[IntelligenceAnomaly]
    recurring: list[IntelligenceRecurringExpense]


class IntelligenceService:
    CENT = Decimal('0.01')
    HUNDRED = Decimal('100.00')
    HISTORY_MONTHS = 6
    ANALYSIS_MONTHS = 12

    def __init__(
        self,
        *,
        repository: ReportRepository,
        report_service: ReportService,
        budget_service: BudgetService,
    ):
        self.repository = repository
        self.report_service = report_service
        self.budget_service = budget_service

    def get_overview(
        self,
        *,
        year: int,
        month: int,
        today: date | None = None,
    ) -> IntelligenceOverview:
        self._validate_period(year=year, month=month)
        reference_date = today or date.today()
        history_start = self._shift_month(year, month, -(self.HISTORY_MONTHS - 1))
        analysis_start = self._shift_month(year, month, -(self.ANALYSIS_MONTHS - 1))

        history = self.report_service.get_overview(
            start_year=history_start[0],
            start_month=history_start[1],
            end_year=year,
            end_month=month,
        )
        current = self.report_service.get_overview(
            start_year=year,
            start_month=month,
            end_year=year,
            end_month=month,
        )
        budget = self.budget_service.get_overview(
            year=year,
            month=month,
            today=reference_date,
        )
        expenses = self.repository.list_for_period(
            start_year=analysis_start[0],
            start_month=analysis_start[1],
            end_year=year,
            end_month=month,
        )

        current_total = current.total_spent
        previous = [
            point.total
            for point in history.monthly
            if (point.year, point.month) != (year, month)
        ]
        historical_average = self._average(previous)
        data_months = sum(1 for value in previous if value > 0)
        forecast_total = self._forecast(
            current_total=current_total,
            historical_average=historical_average,
            year=year,
            month=month,
            today=reference_date,
        )
        trend_percent = self._change_percent(
            current_total,
            historical_average,
        )
        anomalies = self._find_anomalies(
            expenses=expenses,
            year=year,
            month=month,
        )
        recurring = self._find_recurring(expenses)
        insights = self._build_insights(
            current=current,
            budget=budget,
            current_total=current_total,
            forecast_total=forecast_total,
            historical_average=historical_average,
            trend_percent=trend_percent,
            data_months=data_months,
            anomalies=anomalies,
            recurring=recurring,
        )

        return IntelligenceOverview(
            year=year,
            month=month,
            generated_at=datetime.now(),
            summary=IntelligenceSummary(
                current_total=self._money(current_total),
                forecast_total=forecast_total,
                historical_average=historical_average,
                trend_percent=trend_percent,
                installment_commitment=self._money(current.installment_commitment),
                budget_usage_percent=(
                    self._money(budget.usage_percent)
                    if budget.usage_percent is not None
                    else None
                ),
                budget_status=budget.status,
                data_months=data_months,
            ),
            monthly=history.monthly,
            insights=insights,
            anomalies=anomalies,
            recurring=recurring,
        )

    def _forecast(
        self,
        *,
        current_total: Decimal,
        historical_average: Decimal,
        year: int,
        month: int,
        today: date,
    ) -> Decimal:
        if (year, month) != (today.year, today.month):
            return self._money(current_total)

        days_in_month = calendar.monthrange(year, month)[1]
        elapsed_days = max(today.day, 1)
        pace_projection = self._money(
            current_total / Decimal(elapsed_days) * Decimal(days_in_month)
        )

        if historical_average <= 0:
            return max(self._money(current_total), pace_projection)

        blended = self._money(
            pace_projection * Decimal('0.70')
            + historical_average * Decimal('0.30')
        )
        return max(self._money(current_total), blended)

    def _find_anomalies(
        self,
        *,
        expenses: list[Expense],
        year: int,
        month: int,
    ) -> list[IntelligenceAnomaly]:
        by_category: dict[str, list[Decimal]] = {}

        for expense in expenses:
            amount = self._owner_total(expense)
            if amount <= 0:
                continue
            by_category.setdefault(expense.category.name, []).append(amount)

        anomalies: list[IntelligenceAnomaly] = []

        for expense in expenses:
            purchase_date = expense.purchase_date.date()
            if (purchase_date.year, purchase_date.month) != (year, month):
                continue

            amount = self._owner_total(expense)
            values = by_category.get(expense.category.name, [])
            if amount <= 0 or len(values) < 4:
                continue

            median = self._money(statistics.median(values))
            deviations = [abs(value - median) for value in values]
            mad = self._money(statistics.median(deviations))
            threshold = (
                median + max(mad * Decimal('3.00'), Decimal('50.00'))
                if mad > 0
                else max(median * Decimal('2.00'), median + Decimal('50.00'))
            )

            if amount <= threshold or amount <= median * Decimal('1.50'):
                continue

            difference = self._change_percent(amount, median) or Decimal('0.00')
            anomalies.append(
                IntelligenceAnomaly(
                    expense_id=expense.id,
                    purchase_date=purchase_date,
                    purchase_place=expense.purchase_place,
                    category=expense.category.name,
                    amount=amount,
                    category_median=median,
                    difference_percent=difference,
                )
            )

        anomalies.sort(key=lambda item: (-item.difference_percent, -item.amount))
        return anomalies[:8]

    def _find_recurring(
        self,
        expenses: list[Expense],
    ) -> list[IntelligenceRecurringExpense]:
        groups: dict[tuple[str, str], list[Expense]] = {}

        for expense in expenses:
            key = (
                self._normalize(expense.purchase_place),
                expense.category.name,
            )
            groups.setdefault(key, []).append(expense)

        result: list[IntelligenceRecurringExpense] = []

        for (_, category), items in groups.items():
            months = {
                (item.purchase_date.year, item.purchase_date.month)
                for item in items
            }
            if len(items) < 3 or len(months) < 3:
                continue

            ordered = sorted(items, key=lambda item: item.purchase_date)
            amounts = [self._owner_total(item) for item in ordered]
            valid_amounts = [amount for amount in amounts if amount > 0]
            if not valid_amounts:
                continue

            last = ordered[-1]
            last_date = last.purchase_date.date()
            result.append(
                IntelligenceRecurringExpense(
                    purchase_place=last.purchase_place,
                    category=category,
                    occurrences=len(items),
                    average_amount=self._average(valid_amounts),
                    last_purchase_date=last_date,
                    expected_next_date=self._next_month_date(last_date),
                )
            )

        result.sort(key=lambda item: (-item.occurrences, -item.average_amount))
        return result[:8]

    def _build_insights(
        self,
        *,
        current,
        budget,
        current_total: Decimal,
        forecast_total: Decimal,
        historical_average: Decimal,
        trend_percent: Decimal | None,
        data_months: int,
        anomalies: list[IntelligenceAnomaly],
        recurring: list[IntelligenceRecurringExpense],
    ) -> list[IntelligenceInsight]:
        items: list[IntelligenceInsight] = []

        if data_months < 3:
            items.append(IntelligenceInsight(
                code='limited_history',
                kind='data_quality',
                severity='info',
                title='Historico ainda curto',
                message='Ha menos de tres meses com movimentacao para comparar tendencias com seguranca.',
                recommendation='Continue registrando ou importando despesas para melhorar as analises.',
            ))

        if budget.status == 'exceeded':
            items.append(IntelligenceInsight(
                code='budget_exceeded',
                kind='budget',
                severity='critical',
                title='Limite mensal ultrapassado',
                message='Os gastos considerados no mes ja superaram o limite definido no planejamento.',
                recommendation='Revise despesas adiaveis e ajuste o restante do mes.',
            ))
        elif budget.status == 'attention':
            items.append(IntelligenceInsight(
                code='budget_attention',
                kind='budget',
                severity='warning',
                title='Orcamento em zona de atencao',
                message='O percentual utilizado do limite mensal ja exige acompanhamento mais proximo.',
                recommendation='Compare a projecao com o limite e reduza gastos variaveis.',
            ))

        if budget.spending_limit is not None and forecast_total > budget.spending_limit:
            excess = self._money(forecast_total - budget.spending_limit)
            items.append(IntelligenceInsight(
                code='forecast_over_limit',
                kind='forecast',
                severity='warning',
                title='Projecao acima do limite',
                message=f'A projecao deterministica supera o limite mensal em R$ {excess}.',
                recommendation='Use a projecao como alerta, nao como certeza, e acompanhe novos lancamentos.',
            ))

        if trend_percent is not None and trend_percent >= Decimal('15.00'):
            items.append(IntelligenceInsight(
                code='spending_acceleration',
                kind='trend',
                severity='warning',
                title='Gastos acima da media recente',
                message=f'O total do mes esta {trend_percent}% acima da media dos meses anteriores.',
                recommendation='Confira categorias e estabelecimentos que mais puxaram o aumento.',
            ))
        elif trend_percent is not None and trend_percent <= Decimal('-15.00'):
            items.append(IntelligenceInsight(
                code='spending_reduction',
                kind='trend',
                severity='positive',
                title='Reducao frente a media recente',
                message=f'O total do mes esta {abs(trend_percent)}% abaixo da media dos meses anteriores.',
                recommendation='Verifique quais habitos ajudaram e tente preserva-los.',
            ))

        if current.categories and current.categories[0].percentage >= Decimal('45.00'):
            top = current.categories[0]
            items.append(IntelligenceInsight(
                code='category_concentration',
                kind='category',
                severity='info',
                title='Concentracao em uma categoria',
                message=f'{top.name} representa {top.percentage}% do total analisado no mes.',
                recommendation='Confirme se essa concentracao e planejada ou pontual.',
            ))

        if anomalies:
            items.append(IntelligenceInsight(
                code='unusual_expenses',
                kind='anomaly',
                severity='warning',
                title='Lancamentos fora do padrao',
                message=f'Foram encontrados {len(anomalies)} lancamento(s) muito acima do padrao da categoria.',
                recommendation='Revise os valores para confirmar se sao corretos e esperados.',
            ))

        if recurring:
            estimated = self._money(sum((item.average_amount for item in recurring), Decimal('0.00')))
            items.append(IntelligenceInsight(
                code='recurring_commitments',
                kind='recurrence',
                severity='info',
                title='Compromissos recorrentes detectados',
                message=f'Os padroes recorrentes identificados somam cerca de R$ {estimated} por ciclo mensal.',
                recommendation='Considere esse valor ao definir o proximo planejamento.',
            ))

        if not items:
            items.append(IntelligenceInsight(
                code='stable_period',
                kind='summary',
                severity='positive',
                title='Periodo sem alertas relevantes',
                message='Os indicadores analisados nao apontaram desvios importantes neste momento.',
                recommendation='Continue registrando os dados para manter a leitura atualizada.',
            ))

        return items[:8]

    def _owner_total(self, expense: Expense) -> Decimal:
        total = self._money(expense.purchase_value)
        shared = sum(
            (self._money(relation.shared_value) for relation in expense.people),
            Decimal('0.00'),
        )
        return max(total - shared, Decimal('0.00'))

    @classmethod
    def _average(cls, values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal('0.00')
        return cls._money(sum(values, Decimal('0.00')) / Decimal(len(values)))

    @classmethod
    def _change_percent(cls, current: Decimal, baseline: Decimal) -> Decimal | None:
        if baseline <= 0:
            return None
        return cls._money((current - baseline) / baseline * cls.HUNDRED)

    @classmethod
    def _money(cls, value) -> Decimal:
        return Decimal(str(value)).quantize(cls.CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()

    @staticmethod
    def _validate_period(*, year: int, month: int) -> None:
        if year < 2000 or year > 2100:
            raise ValueError('O ano deve estar entre 2000 e 2100.')
        if month < 1 or month > 12:
            raise ValueError('O mes deve estar entre 1 e 12.')

    @staticmethod
    def _shift_month(year: int, month: int, amount: int) -> tuple[int, int]:
        index = year * 12 + (month - 1) + amount
        return index // 12, index % 12 + 1

    @staticmethod
    def _next_month_date(source: date) -> date:
        if source.month == 12:
            year, month = source.year + 1, 1
        else:
            year, month = source.year, source.month + 1
        day = min(source.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
