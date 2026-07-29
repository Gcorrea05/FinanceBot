import logging

from app.events.model import DomainEvent

logger = logging.getLogger(__name__)


class LoggingEventHandler:
    def __call__(self, event: DomainEvent) -> None:
        logger.info(
            "Evento financeiro: %s aggregate=%s:%s",
            event.name,
            event.aggregate_type,
            event.aggregate_id,
        )


class ProjectionRefreshHandler:
    def __init__(self, *, budget_service, report_service):
        self.budget_service = budget_service
        self.report_service = report_service

    def __call__(self, event: DomainEvent) -> None:
        year = event.payload.get("year")
        month = event.payload.get("month")
        if not isinstance(year, int) or not isinstance(month, int):
            return
        if not 1 <= month <= 12:
            return
        try:
            self.budget_service.get_overview(year=year, month=month)
            self.report_service.get_overview(
                start_year=year,
                start_month=month,
                end_year=year,
                end_month=month,
            )
        except Exception:
            logger.exception(
                "Nao foi possivel recalcular as projecoes do evento %s.",
                event.name,
            )
