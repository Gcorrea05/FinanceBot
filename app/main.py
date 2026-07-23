import logging

from rich import print

from app.bot.bot import FinanceBot
from app.database.seed import seed_database
from app.database.session import (
    create_database,
    get_session,
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def initialize_database() -> None:
    print(
        "[cyan]"
        "========================================"
        "[/cyan]"
    )

    print(
        "[cyan]"
        "Inicializando FinanceBot"
        "[/cyan]"
    )

    print(
        "[cyan]"
        "========================================"
        "[/cyan]"
    )

    create_database()

    session = get_session()

    try:
        seed_database(session)

        print(
            "[green]"
            "Banco inicializado com sucesso!"
            "[/green]"
        )

    finally:
        session.close()


def main() -> None:
    configure_logging()
    initialize_database()

    print(
        "[yellow]"
        "Iniciando Telegram..."
        "[/yellow]"
    )

    bot = FinanceBot()
    bot.run()


if __name__ == "__main__":
    main()
