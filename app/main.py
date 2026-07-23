from rich import print

from app.bot.bot import FinanceBot
from app.database.seed import seed_database
from app.database.session import create_database, get_session


def initialize_database():
    print("[cyan]========================================[/cyan]")
    print("[cyan] Inicializando FinanceBot[/cyan]")
    print("[cyan]========================================[/cyan]")

    create_database()

    session = get_session()

    try:
        seed_database(session)
        print("[green]Banco inicializado com sucesso![/green]")
    finally:
        session.close()


def main():

    initialize_database()

    print("[yellow]Iniciando Telegram...[/yellow]")

    bot = FinanceBot()

    bot.run()


if __name__ == "__main__":
    main()