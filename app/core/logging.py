import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.request_context import request_id_context
from app.core.settings import settings


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def _file_handler(path: Path, formatter: logging.Formatter) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=settings.logging.max_bytes,
        backupCount=settings.logging.backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())
    return handler


def configure_logging(component: str = "app") -> None:
    root = logging.getLogger()
    if getattr(root, "_financebot_configured", False):
        return

    level = getattr(logging, settings.logging.level, logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "[request_id=%(request_id)s] %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(RequestContextFilter())

    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(console)

    directory = settings.logging.directory
    try:
        directory.mkdir(parents=True, exist_ok=True)
        root.addHandler(_file_handler(directory / "app.log", formatter))
        if component != "app":
            root.addHandler(
                _file_handler(directory / f"{component}.log", formatter)
            )
    except OSError:
        root.warning("Nao foi possivel criar os arquivos de log.")

    setattr(root, "_financebot_configured", True)
