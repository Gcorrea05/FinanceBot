from telegram.ext import (
    CommandHandler,
    ConversationHandler,
)

from app.bot.bot import FinanceBot
from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    MENU_HELP,
    MENU_RECEIVABLES,
    MENU_RECENT_EXPENSES,
    build_main_menu,
)


VALID_TEST_TOKEN = (
    "123456789:"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    "abcdefghi123456789"
)


def _button_text(button) -> str:
    return getattr(
        button,
        "text",
        str(button),
    )


def main() -> None:
    menu = build_main_menu()

    labels = [
        _button_text(button)
        for row in menu.keyboard
        for button in row
    ]

    expected_labels = [
        MENU_ADD_EXPENSE,
        MENU_RECENT_EXPENSES,
        MENU_RECEIVABLES,
        MENU_HELP,
    ]

    if labels != expected_labels:
        raise RuntimeError(
            (
                "O menu principal nao esta "
                "consolidado corretamente."
            )
        )

    if menu.is_persistent is not True:
        raise RuntimeError(
            "O menu principal nao esta persistente."
        )

    bot = FinanceBot(
        token=VALID_TEST_TOKEN
    )

    handlers = bot.application.handlers[0]

    conversations = [
        handler
        for handler in handlers
        if isinstance(
            handler,
            ConversationHandler,
        )
    ]

    if len(conversations) < 2:
        raise RuntimeError(
            (
                "Os fluxos de despesa e "
                "valores a receber nao foram registrados."
            )
        )

    direct_commands = set()

    for handler in handlers:
        if isinstance(
            handler,
            CommandHandler,
        ):
            direct_commands.update(
                handler.commands
            )

    expected_direct_commands = {
        "start",
        "ultimos",
        "ajuda",
    }

    if direct_commands != expected_direct_commands:
        raise RuntimeError(
            (
                "Comandos diretos inesperados: "
                f"{sorted(direct_commands)}"
            )
        )

    print(
        "[OK] Menu operacional consolidado."
    )
    print(
        "[OK] Menu persistente."
    )
    print(
        "[OK] Consulta rapida de lancamentos registrada."
    )
    print(
        "[OK] Fluxos de cadastro e recebimentos preservados."
    )


if __name__ == "__main__":
    main()
