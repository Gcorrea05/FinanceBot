from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3

from app.core.settings import settings


def database_path() -> Path:
    url = settings.database.url

    if not url.startswith("sqlite:///"):
        raise RuntimeError(
            "A restauracao deste script suporta apenas SQLite."
        )

    return Path(
        url.removeprefix("sqlite:///")
    )


def restore_backup(
    backup: Path,
) -> None:
    if not backup.exists():
        raise RuntimeError(
            f"Backup nao encontrado: {backup}"
        )

    target_path = database_path()
    target_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    for suffix in ("-wal", "-shm"):
        Path(
            f"{target_path}{suffix}"
        ).unlink(
            missing_ok=True
        )

    source = sqlite3.connect(
        f"file:{backup}?mode=ro",
        uri=True,
    )
    target = sqlite3.connect(
        target_path
    )

    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backup",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    restore_backup(args.backup)

    print(
        f"[OK] Banco restaurado: {args.backup}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
