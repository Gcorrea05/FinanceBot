from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    """Erro causado por configuracao ausente ou invalida."""


class TelegramSettings(BaseModel):
    token: str
    timeout_seconds: int
    admin_chat_id: str | None


class DatabaseSettings(BaseModel):
    url: str
    sqlite_foreign_keys: bool
    sqlite_wal_enabled: bool
    sqlite_busy_timeout_ms: int
    sqlite_wal_autocheckpoint: int
    sqlite_synchronous: str
    sqlite_backup_enabled: bool
    sqlite_backup_directory: Path


class ApiSettings(BaseModel):
    title: str
    version: str
    host: str
    port: int
    cors_origins_raw: str

    @property
    def cors_origins(self) -> list[str]:
        return [
            value.strip()
            for value in self.cors_origins_raw.split(",")
            if value.strip()
        ]


class AiSettings(BaseModel):
    enabled: bool
    provider: str
    model: str
    temperature: float
    api_key: str


class SchedulerSettings(BaseModel):
    timezone: str
    tick_seconds: int
    automation_interval_seconds: int
    event_interval_seconds: int
    monthly_report_enabled: bool
    monthly_report_hour: int
    report_directory: Path
    log_cleanup_days: int
    sqlite_backup_hour: int


class LoggingSettings(BaseModel):
    level: str
    directory: Path
    max_bytes: int
    backup_count: int


class SecuritySettings(BaseModel):
    expose_api_docs: bool
    trusted_hosts_raw: str

    @property
    def trusted_hosts(self) -> list[str]:
        return [
            value.strip()
            for value in self.trusted_hosts_raw.split(",")
            if value.strip()
        ]


class Settings(BaseSettings):
    @classmethod
    def from_environment(cls) -> "Settings":
        return cls()

    @classmethod
    def from_env(cls) -> "Settings":
        return cls()

    @classmethod
    def load(cls) -> "Settings":
        return cls()

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.production"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    telegram_token: str = Field("", validation_alias="TELEGRAM_TOKEN")
    telegram_timeout_seconds: int = Field(
        30, validation_alias="TELEGRAM_TIMEOUT_SECONDS", ge=5, le=180
    )
    telegram_admin_chat_id: str | None = Field(
        None, validation_alias="TELEGRAM_ADMIN_CHAT_ID"
    )

    database_url: str = Field(
        "sqlite:///data/finance.db", validation_alias="DATABASE_URL"
    )
    sqlite_foreign_keys: bool = Field(
        True, validation_alias="SQLITE_FOREIGN_KEYS"
    )
    sqlite_wal_enabled: bool = Field(
        True, validation_alias="SQLITE_WAL_ENABLED"
    )
    sqlite_busy_timeout_ms: int = Field(
        10_000,
        validation_alias="SQLITE_BUSY_TIMEOUT_MS",
        ge=1_000,
        le=120_000,
    )
    sqlite_wal_autocheckpoint: int = Field(
        1_000,
        validation_alias="SQLITE_WAL_AUTOCHECKPOINT",
        ge=100,
        le=100_000,
    )
    sqlite_synchronous: str = Field(
        "NORMAL", validation_alias="SQLITE_SYNCHRONOUS"
    )
    sqlite_backup_enabled: bool = Field(
        True, validation_alias="SQLITE_BACKUP_ENABLED"
    )
    sqlite_backup_directory: Path = Field(
        Path("backups/sqlite"),
        validation_alias="SQLITE_BACKUP_DIRECTORY",
    )

    api_title: str = Field("FinanceBot API", validation_alias="API_TITLE")
    api_version: str = Field("1.0.0", validation_alias="API_VERSION")
    api_host: str = Field("127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(8000, validation_alias="API_PORT", ge=1, le=65535)
    api_cors_origins: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="API_CORS_ORIGINS",
    )

    ai_enabled: bool = Field(False, validation_alias="AI_ENABLED")
    ai_provider: str = Field("disabled", validation_alias="AI_PROVIDER")
    ai_model: str = Field("", validation_alias="AI_MODEL")
    ai_temperature: float = Field(
        0.2, validation_alias="AI_TEMPERATURE", ge=0, le=2
    )
    ai_api_key: str = Field("", validation_alias="AI_API_KEY")

    scheduler_timezone: str = Field(
        "America/Sao_Paulo", validation_alias="SCHEDULER_TIMEZONE"
    )
    scheduler_tick_seconds: int = Field(
        1, validation_alias="SCHEDULER_TICK_SECONDS", ge=1, le=60
    )
    automation_poll_interval_seconds: int = Field(
        60, validation_alias="AUTOMATION_POLL_INTERVAL_SECONDS", ge=30
    )
    event_poll_interval_seconds: int = Field(
        15, validation_alias="EVENT_POLL_INTERVAL_SECONDS", ge=5
    )
    monthly_report_enabled: bool = Field(
        True, validation_alias="MONTHLY_REPORT_ENABLED"
    )
    monthly_report_hour: int = Field(
        7, validation_alias="MONTHLY_REPORT_HOUR", ge=0, le=23
    )
    report_directory: Path = Field(
        Path("data/reports"), validation_alias="REPORT_DIRECTORY"
    )
    log_cleanup_days: int = Field(
        30, validation_alias="LOG_CLEANUP_DAYS", ge=1
    )
    sqlite_backup_hour: int = Field(
        3, validation_alias="SQLITE_BACKUP_HOUR", ge=0, le=23
    )

    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    log_directory: Path = Field(Path("logs"), validation_alias="LOG_DIRECTORY")
    log_max_bytes: int = Field(
        5_000_000, validation_alias="LOG_MAX_BYTES", ge=100_000
    )
    log_backup_count: int = Field(
        5, validation_alias="LOG_BACKUP_COUNT", ge=1, le=50
    )

    expose_api_docs: bool = Field(True, validation_alias="EXPOSE_API_DOCS")
    trusted_hosts: str = Field(
        "localhost,127.0.0.1,testserver", validation_alias="TRUSTED_HOSTS"
    )

    @property
    def telegram(self) -> TelegramSettings:
        return TelegramSettings(
            token=self.telegram_token.strip(),
            timeout_seconds=self.telegram_timeout_seconds,
            admin_chat_id=self.telegram_admin_chat_id,
        )

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            url=self.database_url,
            sqlite_foreign_keys=self.sqlite_foreign_keys,
            sqlite_wal_enabled=self.sqlite_wal_enabled,
            sqlite_busy_timeout_ms=self.sqlite_busy_timeout_ms,
            sqlite_wal_autocheckpoint=self.sqlite_wal_autocheckpoint,
            sqlite_synchronous=self.sqlite_synchronous.upper(),
            sqlite_backup_enabled=self.sqlite_backup_enabled,
            sqlite_backup_directory=self.sqlite_backup_directory,
        )

    @property
    def api(self) -> ApiSettings:
        return ApiSettings(
            title=self.api_title,
            version=self.api_version,
            host=self.api_host,
            port=self.api_port,
            cors_origins_raw=self.api_cors_origins,
        )

    @property
    def ai(self) -> AiSettings:
        return AiSettings(
            enabled=self.ai_enabled,
            provider=self.ai_provider,
            model=self.ai_model,
            temperature=self.ai_temperature,
            api_key=self.ai_api_key,
        )

    @property
    def scheduler(self) -> SchedulerSettings:
        return SchedulerSettings(
            timezone=self.scheduler_timezone,
            tick_seconds=self.scheduler_tick_seconds,
            automation_interval_seconds=self.automation_poll_interval_seconds,
            event_interval_seconds=self.event_poll_interval_seconds,
            monthly_report_enabled=self.monthly_report_enabled,
            monthly_report_hour=self.monthly_report_hour,
            report_directory=self.report_directory,
            log_cleanup_days=self.log_cleanup_days,
            sqlite_backup_hour=self.sqlite_backup_hour,
        )

    @property
    def logging(self) -> LoggingSettings:
        return LoggingSettings(
            level=self.log_level.upper(),
            directory=self.log_directory,
            max_bytes=self.log_max_bytes,
            backup_count=self.log_backup_count,
        )

    @property
    def security(self) -> SecuritySettings:
        return SecuritySettings(
            expose_api_docs=self.expose_api_docs,
            trusted_hosts_raw=self.trusted_hosts,
        )

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def TELEGRAM_TOKEN(self) -> str:
        return self.telegram_token

    def require_telegram_token(self) -> str:
        token = self.telegram_token.strip()
        if not token:
            raise ConfigurationError("TELEGRAM_TOKEN nao configurado.")
        return token


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
