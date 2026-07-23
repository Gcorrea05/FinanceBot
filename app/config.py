import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when a required application setting is missing."""

    pass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///data/finance.db",
    )

    TELEGRAM_TOKEN: str = os.getenv(
        "TELEGRAM_TOKEN",
        "",
    )

    def require_telegram_token(self) -> str:
        token = self.TELEGRAM_TOKEN.strip()

        if not token:
            raise ConfigurationError(
                "TELEGRAM_TOKEN nao foi configurado no arquivo .env."
            )

        return token


settings = Settings()
