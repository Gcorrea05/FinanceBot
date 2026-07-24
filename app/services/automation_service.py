from __future__ import annotations

from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from typing import (
    TYPE_CHECKING,
    Protocol,
)
from zoneinfo import (
    ZoneInfo,
    ZoneInfoNotFoundError,
)

if TYPE_CHECKING:
    from app.database.models import (
        AutomationDelivery,
        AutomationSettings,
        Expense,
        ExpenseInstallment,
    )
    from app.repositories.automation_repository import (
        AutomationRepository,
    )
    from app.services.budget_service import (
        BudgetService,
    )


class NotificationSender(Protocol):
    async def send(
        self,
        *,
        chat_id: str,
        message: str,
    ) -> None:
        ...


@dataclass(frozen=True)
class AutomationSettingsView:
    enabled: bool
    telegram_connected: bool
    timezone: str
    daily_summary_enabled: bool
    daily_summary_hour: int
    weekly_summary_enabled: bool
    weekly_summary_weekday: int
    weekly_summary_hour: int
    installment_reminders_enabled: bool
    installment_reminder_days: int
    reminder_hour: int
    budget_alerts_enabled: bool
    budget_alert_threshold: int


@dataclass(frozen=True)
class AutomationEvent:
    kind: str
    title: str
    message: str
    deduplication_key: str
    scheduled_for: datetime | None


@dataclass(frozen=True)
class AutomationRunResult:
    generated: int
    sent: int
    skipped: int
    failed: int
    events: list[AutomationEvent]


class AutomationService:
    CENT = Decimal("0.01")
    DEFAULT_TIMEZONE = (
        "America/Sao_Paulo"
    )

    def __init__(
        self,
        *,
        repository: AutomationRepository,
        budget_service: BudgetService,
    ):
        self.repository = repository
        self.budget_service = budget_service

    def get_settings(
        self,
    ) -> AutomationSettingsView:
        return self._settings_view(
            self.repository.get_settings()
        )

    def save_settings(
        self,
        *,
        enabled: bool,
        timezone: str,
        daily_summary_enabled: bool,
        daily_summary_hour: int,
        weekly_summary_enabled: bool,
        weekly_summary_weekday: int,
        weekly_summary_hour: int,
        installment_reminders_enabled: bool,
        installment_reminder_days: int,
        reminder_hour: int,
        budget_alerts_enabled: bool,
        budget_alert_threshold: int,
    ) -> AutomationSettingsView:
        normalized_timezone = (
            timezone.strip()
        )

        self._validate_timezone(
            normalized_timezone
        )
        self._validate_hour(
            daily_summary_hour,
            "Hora do resumo diario",
        )
        self._validate_hour(
            weekly_summary_hour,
            "Hora do resumo semanal",
        )
        self._validate_hour(
            reminder_hour,
            "Hora dos lembretes",
        )

        if not 0 <= weekly_summary_weekday <= 6:
            raise ValueError(
                (
                    "O dia do resumo semanal "
                    "deve ficar entre 0 e 6."
                )
            )

        if not 0 <= installment_reminder_days <= 30:
            raise ValueError(
                (
                    "A antecedencia deve ficar "
                    "entre 0 e 30 dias."
                )
            )

        if not 1 <= budget_alert_threshold <= 100:
            raise ValueError(
                (
                    "O limite de alerta deve "
                    "ficar entre 1 e 100."
                )
            )

        saved = self.repository.save_settings(
            enabled=enabled,
            timezone=normalized_timezone,
            daily_summary_enabled=(
                daily_summary_enabled
            ),
            daily_summary_hour=(
                daily_summary_hour
            ),
            weekly_summary_enabled=(
                weekly_summary_enabled
            ),
            weekly_summary_weekday=(
                weekly_summary_weekday
            ),
            weekly_summary_hour=(
                weekly_summary_hour
            ),
            installment_reminders_enabled=(
                installment_reminders_enabled
            ),
            installment_reminder_days=(
                installment_reminder_days
            ),
            reminder_hour=reminder_hour,
            budget_alerts_enabled=(
                budget_alerts_enabled
            ),
            budget_alert_threshold=(
                budget_alert_threshold
            ),
        )

        return self._settings_view(saved)

    def link_telegram_chat(
        self,
        chat_id: int | str,
    ) -> AutomationSettingsView:
        normalized = str(
            chat_id
        ).strip()

        if not normalized:
            raise ValueError(
                "Chat do Telegram invalido."
            )

        settings = (
            self.repository.link_chat(
                normalized
            )
        )

        return self._settings_view(
            settings
        )

    def disconnect_telegram(
        self,
    ) -> AutomationSettingsView:
        return self._settings_view(
            self.repository
            .disconnect_chat()
        )

    def preview(
        self,
        *,
        now: datetime | None = None,
    ) -> list[AutomationEvent]:
        settings = (
            self.repository.get_settings()
        )
        view = self._settings_view(
            settings
        )
        local_now = self._local_now(
            now=now,
            timezone=view.timezone,
        )

        events: list[
            AutomationEvent
        ] = []

        if view.daily_summary_enabled:
            events.append(
                self._daily_summary_event(
                    local_now
                )
            )

        if view.weekly_summary_enabled:
            events.append(
                self._weekly_summary_event(
                    local_now
                )
            )

        if (
            view.installment_reminders_enabled
        ):
            reminder = (
                self._installment_event(
                    local_now,
                    view
                    .installment_reminder_days,
                )
            )

            if reminder is not None:
                events.append(reminder)

        if view.budget_alerts_enabled:
            budget = self._budget_event(
                local_now,
                view
                .budget_alert_threshold,
            )

            if budget is not None:
                events.append(budget)

        return events

    async def run_due(
        self,
        *,
        sender: NotificationSender,
        now: datetime | None = None,
        force: bool = False,
    ) -> AutomationRunResult:
        settings = (
            self.repository.get_settings()
        )
        view = self._settings_view(
            settings
        )
        local_now = self._local_now(
            now=now,
            timezone=view.timezone,
        )

        if not view.enabled and not force:
            return AutomationRunResult(
                generated=0,
                sent=0,
                skipped=0,
                failed=0,
                events=[],
            )

        chat_id = (
            settings.telegram_chat_id
            if settings is not None
            else None
        )

        if not chat_id:
            raise ValueError(
                (
                    "Telegram nao vinculado. "
                    "Envie /notificacoes ao bot."
                )
            )

        events = (
            self.preview(now=local_now)
            if force
            else self._scheduled_events(
                local_now=local_now,
                settings=view,
            )
        )

        sent = 0
        skipped = 0
        failed = 0

        for event in events:
            key = event.deduplication_key

            if force:
                key = (
                    f"manual:{local_now.isoformat()}:"
                    f"{event.kind}"
                )

            if (
                not force
                and self.repository
                .delivery_exists(key)
            ):
                skipped += 1
                continue

            try:
                await sender.send(
                    chat_id=chat_id,
                    message=event.message,
                )
            except Exception as error:
                failed += 1
                self.repository.record_delivery(
                    kind=event.kind,
                    deduplication_key=key,
                    status="failed",
                    message=event.message,
                    scheduled_for=(
                        event.scheduled_for
                    ),
                    error_message=str(error),
                )
            else:
                sent += 1
                self.repository.record_delivery(
                    kind=event.kind,
                    deduplication_key=key,
                    status="sent",
                    message=event.message,
                    scheduled_for=(
                        event.scheduled_for
                    ),
                    sent_at=(
                        datetime.now(
                            timezone.utc
                        ).replace(
                            tzinfo=None
                        )
                    ),
                )

        return AutomationRunResult(
            generated=len(events),
            sent=sent,
            skipped=skipped,
            failed=failed,
            events=events,
        )

    def list_deliveries(
        self,
        limit: int = 30,
    ) -> list[AutomationDelivery]:
        return (
            self.repository
            .list_deliveries(limit=limit)
        )

    def _scheduled_events(
        self,
        *,
        local_now: datetime,
        settings: AutomationSettingsView,
    ) -> list[AutomationEvent]:
        events: list[
            AutomationEvent
        ] = []

        if (
            settings.daily_summary_enabled
            and local_now.hour
            == settings.daily_summary_hour
        ):
            events.append(
                self._daily_summary_event(
                    local_now
                )
            )

        if (
            settings.weekly_summary_enabled
            and local_now.weekday()
            == settings
            .weekly_summary_weekday
            and local_now.hour
            == settings.weekly_summary_hour
        ):
            events.append(
                self._weekly_summary_event(
                    local_now
                )
            )

        if (
            settings
            .installment_reminders_enabled
            and local_now.hour
            == settings.reminder_hour
        ):
            reminder = (
                self._installment_event(
                    local_now,
                    settings
                    .installment_reminder_days,
                )
            )

            if reminder is not None:
                events.append(reminder)

        if settings.budget_alerts_enabled:
            budget = self._budget_event(
                local_now,
                settings
                .budget_alert_threshold,
            )

            if budget is not None:
                events.append(budget)

        return events

    def _daily_summary_event(
        self,
        local_now: datetime,
    ) -> AutomationEvent:
        day_start = datetime.combine(
            local_now.date(),
            time.min,
        )
        day_end = (
            day_start
            + timedelta(days=1)
        )
        expenses = (
            self.repository
            .list_expenses_between(
                start=day_start,
                end=day_end,
            )
        )
        total = self._expenses_total(
            expenses
        )
        budget = (
            self.budget_service
            .get_overview(
                year=local_now.year,
                month=local_now.month,
                today=local_now.date(),
            )
        )
        receivables = self._money(
            self.repository
            .pending_receivables_total()
        )

        lines = [
            "FinanceBot - resumo diario",
            "",
            (
                f"Hoje: {len(expenses)} "
                f"lancamento(s), "
                f"{self._currency(total)}."
            ),
            (
                "A receber: "
                f"{self._currency(receivables)}."
            ),
        ]

        if (
            budget.configured
            and budget.usage_percent
            is not None
        ):
            lines.append(
                (
                    "Planejamento: "
                    f"{budget.usage_percent}% "
                    "do limite utilizado."
                )
            )
        else:
            lines.append(
                (
                    "Planejamento do mes "
                    "ainda nao configurado."
                )
            )

        target = datetime.combine(
            local_now.date(),
            time(
                hour=local_now.hour
            ),
        )

        return AutomationEvent(
            kind="daily_summary",
            title="Resumo diario",
            message="\n".join(lines),
            deduplication_key=(
                "daily:"
                f"{local_now.date().isoformat()}"
            ),
            scheduled_for=target,
        )

    def _weekly_summary_event(
        self,
        local_now: datetime,
    ) -> AutomationEvent:
        end = datetime.combine(
            local_now.date()
            + timedelta(days=1),
            time.min,
        )
        start = (
            end
            - timedelta(days=7)
        )
        expenses = (
            self.repository
            .list_expenses_between(
                start=start,
                end=end,
            )
        )
        total = self._expenses_total(
            expenses
        )
        categories: dict[
            str,
            Decimal,
        ] = {}

        for expense in expenses:
            name = (
                expense.category.name
                if expense.category
                is not None
                else "Sem categoria"
            )
            categories[name] = (
                categories.get(
                    name,
                    Decimal("0.00"),
                )
                + self._owner_total(
                    expense
                )
            )

        top_category = (
            max(
                categories.items(),
                key=lambda item: item[1],
            )
            if categories
            else None
        )

        lines = [
            "FinanceBot - resumo semanal",
            "",
            (
                f"Ultimos 7 dias: "
                f"{len(expenses)} "
                f"lancamento(s), "
                f"{self._currency(total)}."
            ),
        ]

        if top_category is not None:
            lines.append(
                (
                    "Maior categoria: "
                    f"{top_category[0]} "
                    f"({self._currency(top_category[1])})."
                )
            )

        week_key = (
            f"{local_now.isocalendar().year}-"
            f"W{local_now.isocalendar().week:02d}"
        )

        return AutomationEvent(
            kind="weekly_summary",
            title="Resumo semanal",
            message="\n".join(lines),
            deduplication_key=(
                f"weekly:{week_key}"
            ),
            scheduled_for=local_now.replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        )

    def _installment_event(
        self,
        local_now: datetime,
        reminder_days: int,
    ) -> AutomationEvent | None:
        end_date = (
            local_now.date()
            + timedelta(
                days=reminder_days
            )
        )
        installments = (
            self.repository
            .list_unpaid_installments_until(
                end_date=end_date
            )
        )

        if not installments:
            return None

        lines = [
            (
                "FinanceBot - "
                "parcelas e vencimentos"
            ),
            "",
        ]

        for item in installments[:10]:
            owner_value = (
                self._owner_installment(
                    item
                )
            )
            due_label = self._due_label(
                item.due_date,
                local_now.date(),
            )
            place = (
                item.expense
                .purchase_place
            )

            lines.append(
                (
                    f"- {place}: "
                    f"{self._currency(owner_value)} "
                    f"({due_label})"
                )
            )

        if len(installments) > 10:
            lines.append(
                (
                    f"... e mais "
                    f"{len(installments) - 10} "
                    "parcela(s)."
                )
            )

        return AutomationEvent(
            kind="installment_reminder",
            title="Vencimentos",
            message="\n".join(lines),
            deduplication_key=(
                "installments:"
                f"{local_now.date().isoformat()}"
            ),
            scheduled_for=local_now.replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        )

    def _budget_event(
        self,
        local_now: datetime,
        threshold: int,
    ) -> AutomationEvent | None:
        overview = (
            self.budget_service
            .get_overview(
                year=local_now.year,
                month=local_now.month,
                today=local_now.date(),
            )
        )

        if (
            not overview.configured
            or overview.usage_percent
            is None
        ):
            return None

        usage = overview.usage_percent

        if usage >= Decimal("100.00"):
            level = 100
            title = "Limite ultrapassado"
        elif usage >= Decimal(
            str(threshold)
        ):
            level = threshold
            title = "Atencao ao limite"
        else:
            return None

        remaining = (
            overview.remaining
            if overview.remaining
            is not None
            else Decimal("0.00")
        )

        message = "\n".join(
            [
                f"FinanceBot - {title}",
                "",
                (
                    f"Voce utilizou "
                    f"{usage}% do limite "
                    "do mes."
                ),
                (
                    "Saldo do limite: "
                    f"{self._currency(remaining)}."
                ),
            ]
        )

        return AutomationEvent(
            kind="budget_alert",
            title=title,
            message=message,
            deduplication_key=(
                "budget:"
                f"{local_now.year}-"
                f"{local_now.month:02d}:"
                f"{level}"
            ),
            scheduled_for=local_now,
        )

    @classmethod
    def _expenses_total(
        cls,
        expenses: list[Expense],
    ) -> Decimal:
        return sum(
            (
                cls._owner_total(
                    expense
                )
                for expense in expenses
            ),
            start=Decimal("0.00"),
        ).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def _owner_total(
        cls,
        expense: Expense,
    ) -> Decimal:
        purchase = cls._money(
            expense.purchase_value
        )
        shared = sum(
            (
                cls._money(
                    relation.shared_value
                )
                for relation
                in expense.people
            ),
            start=Decimal("0.00"),
        )

        return max(
            purchase - shared,
            Decimal("0.00"),
        ).quantize(cls.CENT)

    @classmethod
    def _owner_installment(
        cls,
        installment: ExpenseInstallment,
    ) -> Decimal:
        expense = installment.expense
        purchase = cls._money(
            expense.purchase_value
        )

        if purchase <= 0:
            return Decimal("0.00")

        owner = cls._owner_total(
            expense
        )
        ratio = owner / purchase

        return (
            cls._money(
                installment.installment_value
            )
            * ratio
        ).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:
        return Decimal(
            str(value or 0)
        ).quantize(
            cls.CENT,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _currency(
        value: Decimal,
    ) -> str:
        quantized = value.quantize(
            Decimal("0.01")
        )
        raw = f"{quantized:,.2f}"

        return (
            "R$ "
            + raw
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )

    @staticmethod
    def _due_label(
        due_date: date,
        today: date,
    ) -> str:
        delta = (
            due_date - today
        ).days

        if delta < 0:
            return (
                f"atrasada ha "
                f"{abs(delta)} dia(s)"
            )

        if delta == 0:
            return "vence hoje"

        if delta == 1:
            return "vence amanha"

        return (
            f"vence em {delta} dias"
        )

    @classmethod
    def _settings_view(
        cls,
        settings: AutomationSettings | None,
    ) -> AutomationSettingsView:
        if settings is None:
            return AutomationSettingsView(
                enabled=False,
                telegram_connected=False,
                timezone=(
                    cls.DEFAULT_TIMEZONE
                ),
                daily_summary_enabled=True,
                daily_summary_hour=20,
                weekly_summary_enabled=True,
                weekly_summary_weekday=0,
                weekly_summary_hour=8,
                installment_reminders_enabled=True,
                installment_reminder_days=3,
                reminder_hour=9,
                budget_alerts_enabled=True,
                budget_alert_threshold=80,
            )

        return AutomationSettingsView(
            enabled=settings.enabled,
            telegram_connected=bool(
                settings.telegram_chat_id
            ),
            timezone=settings.timezone,
            daily_summary_enabled=(
                settings
                .daily_summary_enabled
            ),
            daily_summary_hour=(
                settings.daily_summary_hour
            ),
            weekly_summary_enabled=(
                settings
                .weekly_summary_enabled
            ),
            weekly_summary_weekday=(
                settings
                .weekly_summary_weekday
            ),
            weekly_summary_hour=(
                settings
                .weekly_summary_hour
            ),
            installment_reminders_enabled=(
                settings
                .installment_reminders_enabled
            ),
            installment_reminder_days=(
                settings
                .installment_reminder_days
            ),
            reminder_hour=(
                settings.reminder_hour
            ),
            budget_alerts_enabled=(
                settings
                .budget_alerts_enabled
            ),
            budget_alert_threshold=(
                settings
                .budget_alert_threshold
            ),
        )

    @staticmethod
    def _local_now(
        *,
        now: datetime | None,
        timezone: str,
    ) -> datetime:
        zone = ZoneInfo(timezone)

        if now is None:
            return datetime.now(zone)

        if now.tzinfo is None:
            return now.replace(
                tzinfo=zone
            )

        return now.astimezone(zone)

    @staticmethod
    def _validate_timezone(
        timezone: str,
    ) -> None:
        try:
            ZoneInfo(timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError(
                (
                    "Fuso horario invalido. "
                    "Use um nome IANA, como "
                    "America/Sao_Paulo."
                )
            ) from error

    @staticmethod
    def _validate_hour(
        value: int,
        label: str,
    ) -> None:
        if not 0 <= value <= 23:
            raise ValueError(
                (
                    f"{label} deve ficar "
                    "entre 0 e 23."
                )
            )
