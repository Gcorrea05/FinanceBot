import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from time import monotonic

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScheduledJob:
    name: str
    interval_seconds: int
    callback: Callable[[], Awaitable[None]]
    run_on_start: bool = False


class SchedulerRunner:
    def __init__(
        self,
        *,
        jobs: list[ScheduledJob],
        tick_seconds: int = 1,
    ):
        self.jobs = jobs
        self.tick_seconds = max(tick_seconds, 1)

    async def run_forever(self) -> None:
        now = monotonic()
        next_runs = {
            job.name: (
                now
                if job.run_on_start
                else now + job.interval_seconds
            )
            for job in self.jobs
        }
        logger.info("Scheduler iniciado com %s job(s).", len(self.jobs))

        while True:
            current = monotonic()
            for job in self.jobs:
                if current < next_runs[job.name]:
                    continue
                try:
                    await job.callback()
                except Exception:
                    logger.exception("Falha no job %s.", job.name)
                finally:
                    next_runs[job.name] = (
                        monotonic() + max(job.interval_seconds, 1)
                    )
            await asyncio.sleep(self.tick_seconds)
