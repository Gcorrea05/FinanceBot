import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    title: str = "FinanceBot API"
    version: str = "0.1.0"
    host: str = os.getenv(
        "API_HOST",
        "127.0.0.1",
    )
    port: int = int(
        os.getenv(
            "API_PORT",
            "8000",
        )
    )
    cors_origins_raw: str = os.getenv(
        "API_CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]


api_settings = ApiSettings()
