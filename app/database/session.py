from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.base import Base

# Cria a pasta data automaticamente
Path("data").mkdir(exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


def create_database():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()