from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import models as _models
from app.database.base import Base


def _prepare_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    raw_path = database_url.removeprefix("sqlite:///")
    if raw_path == ":memory:":
        return
    Path(raw_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


_prepare_sqlite_directory(settings.DATABASE_URL)

connect_args: dict[str, object] = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "timeout": settings.database.sqlite_busy_timeout_ms / 1000,
        "check_same_thread": False,
    }

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def create_database() -> None:
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
