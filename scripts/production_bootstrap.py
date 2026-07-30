from __future__ import annotations

from scripts.bootstrap_migrations import main as migrate
from scripts.seed_batch17_financial_data import main as seed
from scripts.validate_database import main as validate


def main() -> int:
    if migrate() != 0:
        return 1
    if seed() != 0:
        return 1
    return validate()


if __name__ == "__main__":
    raise SystemExit(main())
