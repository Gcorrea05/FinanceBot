from sqlalchemy import Engine, event

from app.core.settings import settings

_installed = False


def install_sqlite_foreign_keys() -> None:
    """Install the SQLite safety pragmas on every DB-API connection."""
    global _installed
    if _installed:
        return

    @event.listens_for(Engine, "connect")
    def _configure_sqlite(dbapi_connection, _connection_record) -> None:
        module_name = dbapi_connection.__class__.__module__
        if not module_name.startswith("sqlite3"):
            return

        database = settings.database
        cursor = dbapi_connection.cursor()
        try:
            if database.sqlite_foreign_keys:
                cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute(f"PRAGMA busy_timeout={database.sqlite_busy_timeout_ms}")
            cursor.execute(
                f"PRAGMA wal_autocheckpoint={database.sqlite_wal_autocheckpoint}"
            )
            synchronous = database.sqlite_synchronous
            if synchronous not in {"OFF", "NORMAL", "FULL", "EXTRA"}:
                synchronous = "NORMAL"
            cursor.execute(f"PRAGMA synchronous={synchronous}")
            cursor.execute("PRAGMA temp_store=MEMORY")
            if database.sqlite_wal_enabled:
                cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()

    _installed = True


install_sqlite_foreign_keys()
