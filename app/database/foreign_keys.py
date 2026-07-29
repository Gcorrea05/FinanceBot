from sqlalchemy import Engine, event

from app.core.settings import settings

_installed = False


def install_sqlite_foreign_keys() -> None:
    global _installed
    if _installed or not settings.database.sqlite_foreign_keys:
        return

    @event.listens_for(Engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        module_name = dbapi_connection.__class__.__module__
        if not module_name.startswith("sqlite3"):
            return
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    _installed = True


install_sqlite_foreign_keys()
