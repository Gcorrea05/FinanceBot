from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import models as _models
from app.database.base import Base


Path("data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def create_database() -> None:
    """Cria todas as tabelas registradas nos models."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Cria uma nova sessao de banco de dados."""
    return SessionLocal()