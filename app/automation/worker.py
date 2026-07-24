import asyncio
import logging
import os

from dotenv import load_dotenv

from app.container import (
    container_context,
)
from app.notifications import (
    TelegramNotifier,
)


logger = logging.getLogger(
    __name__
)


async def run_worker() -> None:
    load_dotenv()

    token = os.getenv(
        "TELEGRAM_TOKEN",
        "",
    ).strip()

    if not token:
        raise RuntimeError(
            "TELEGRAM_TOKEN nao configurado."
        )

    interval = int(
        os.getenv(
            (
                "AUTOMATION_POLL_"
                "INTERVAL_SECONDS"
            ),
            "60",
        )
    )

    interval = max(
        interval,
        30,
    )
    sender = TelegramNotifier(
        token
    )

    logger.info(
        (
            "Worker de automacoes "
            "iniciado. Intervalo: %s s."
        ),
        interval,
    )

    while True:
        try:
            with container_context() as container:
                result = await (
                    container
                    .automation_service
                    .run_due(
                        sender=sender
                    )
                )

            if (
                result.sent
                or result.failed
            ):
                logger.info(
                    (
                        "Automacoes: "
                        "%s enviadas, "
                        "%s falhas."
                    ),
                    result.sent,
                    result.failed,
                )
        except Exception:
            logger.exception(
                (
                    "Falha ao executar "
                    "as automacoes."
                )
            )

        await asyncio.sleep(
            interval
        )


def main() -> None:
    logging.basicConfig(
        level=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ),
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s: %(message)s"
        ),
    )

    asyncio.run(
        run_worker()
    )


if __name__ == "__main__":
    main()
