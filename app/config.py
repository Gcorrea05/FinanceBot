import os

from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///data/finance.db"
    )

    TELEGRAM_TOKEN: str = os.getenv(
        "TELEGRAM_TOKEN",
        ""
    )


settings = Settings()