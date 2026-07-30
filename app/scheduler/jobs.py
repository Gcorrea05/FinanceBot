from datetime import datetime, timedelta
import logging
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.container import container_context
from app.core.settings import settings
from app.scheduler.registry import ScheduledJob

logger = logging.getLogger(__name__)


def _local_now() -> datetime:
    try:
        timezone = ZoneInfo(settings.scheduler.timezone)
    except ZoneInfoNotFoundError:
        timezone = ZoneInfo("UTC")
    return datetime.now(timezone)


async def _run_automations(sender) -> None:
    if sender is None:
        logger.warning("Automacoes Telegram ignoradas: token ausente.")
        return
    with container_context() as container:
        result = await container.automation_service.run_due(sender=sender)
    if result.sent or result.failed:
        logger.info(
            "Automacoes: %s enviadas, %s falhas.",
            result.sent,
            result.failed,
        )


async def _run_events() -> None:
    with container_context() as container:
        processed, failed = container.event_dispatcher.process_pending(
            limit=100
        )
    if processed or failed:
        logger.info(
            "Eventos: %s processados, %s falhas.",
            processed,
            failed,
        )


async def _run_recurring_expenses() -> None:
    with container_context() as container:
        profile = container.financial_profile_repository.get_or_create_default()
        created = container.recurring_expense_service.materialize(
            months=profile.projection_months,
        )
        posted = container.recurring_expense_service.post_due()
    if created or posted:
        logger.info(
            "Recorrencias: %s ocorrencias criadas, %s lancadas.",
            created,
            posted,
        )


async def _monthly_report() -> None:
    scheduler = settings.scheduler
    if not scheduler.monthly_report_enabled:
        return
    now = _local_now()
    if now.day != 1 or now.hour < scheduler.monthly_report_hour:
        return

    previous = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - timedelta(days=1)

    directory = scheduler.report_directory
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (
        f"financebot_relatorio_{previous.year}_{previous.month:02d}.xlsx"
    )
    if target.exists():
        return

    with container_context() as container:
        content, _filename = container.monthly_export_service.build(
            year=previous.year,
            month=previous.month,
        )
    target.write_bytes(content)
    logger.info("Relatorio mensal gerado: %s", target)


async def _cleanup_logs() -> None:
    directory = settings.logging.directory
    if not directory.exists():
        return
    cutoff = (
        datetime.now().timestamp()
        - settings.scheduler.log_cleanup_days * 86400
    )
    removed = 0
    for path in directory.glob("*.log.*"):
        if path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            removed += 1
    if removed:
        logger.info("%s log(s) antigo(s) removido(s).", removed)


async def _backup_sqlite() -> None:
    database = settings.database
    if not (
        database.sqlite_backup_enabled
        and database.url.startswith("sqlite:///")
    ):
        return
    now = _local_now()
    if now.hour < settings.scheduler.sqlite_backup_hour:
        return

    source_path = Path(database.url.removeprefix("sqlite:///"))
    if not source_path.exists():
        return
    directory = database.sqlite_backup_directory
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"finance-{now:%Y%m%d}.db"
    if target.exists():
        return
    source = sqlite3.connect(
        f"file:{source_path}?mode=ro",
        uri=True,
        timeout=database.sqlite_busy_timeout_ms / 1000,
    )
    backup = sqlite3.connect(target)
    try:
        source.backup(backup)
        result = backup.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise RuntimeError("O backup SQLite falhou na verificacao de integridade.")
    finally:
        backup.close()
        source.close()
    logger.info("Backup SQLite criado: %s", target)


def build_scheduler_jobs(*, sender) -> list[ScheduledJob]:
    async def automations() -> None:
        await _run_automations(sender)

    return [
        ScheduledJob(
            name="domain-events",
            interval_seconds=settings.scheduler.event_interval_seconds,
            callback=_run_events,
            run_on_start=True,
        ),
        ScheduledJob(
            name="recurring-expenses",
            interval_seconds=3600,
            callback=_run_recurring_expenses,
            run_on_start=True,
        ),
        ScheduledJob(
            name="automations",
            interval_seconds=settings.scheduler.automation_interval_seconds,
            callback=automations,
            run_on_start=True,
        ),
        ScheduledJob(
            name="monthly-report",
            interval_seconds=3600,
            callback=_monthly_report,
            run_on_start=True,
        ),
        ScheduledJob(
            name="log-cleanup",
            interval_seconds=3600,
            callback=_cleanup_logs,
            run_on_start=True,
        ),
        ScheduledJob(
            name="sqlite-backup",
            interval_seconds=3600,
            callback=_backup_sqlite,
            run_on_start=True,
        ),
    ]
