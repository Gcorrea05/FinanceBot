from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3

from app.core.settings import settings


def database_path() -> Path:
    url = settings.database.url

    if not url.startswith("sqlite:///"):
        raise RuntimeError(
            "O backup deste script suporta apenas SQLite."
        )

    return Path(
        url.removeprefix("sqlite:///")
    )


def create_backup(
    output: Path,
) -> None:
    source_path = database_path()

    if not source_path.exists():
        raise RuntimeError(
            f"Banco nao encontrado: {source_path}"
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source = sqlite3.connect(
        f"file:{source_path}?mode=ro",
        uri=True,
    )
    target = sqlite3.connect(output)

    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    create_backup(args.output)

    print(
        f"[OK] Backup SQLite criado: {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
