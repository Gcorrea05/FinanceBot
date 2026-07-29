import asyncio
import logging

from app.core.logging import configure_logging
from app.core.settings import settings
from app.notifications import TelegramNotifier
from app.scheduler import SchedulerRunner, build_scheduler_jobs

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    token = settings.telegram.token
    sender = TelegramNotifier(token) if token else None
    runner = SchedulerRunner(
        jobs=build_scheduler_jobs(sender=sender),
        tick_seconds=settings.scheduler.tick_seconds,
    )
    await runner.run_forever()


def main() -> None:
    configure_logging("scheduler")
    logger.info("Worker geral iniciado.")
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
