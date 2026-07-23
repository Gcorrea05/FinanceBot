import sys
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from telegram.ext import ConversationHandler

from app.bot.bot import FinanceBot


VALID_TEST_TOKEN = (
    "123456789:"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    "abcdefghi123456789"
)


def main() -> None:
    bot = FinanceBot(
        token=VALID_TEST_TOKEN
    )

    handlers = (
        bot.application.handlers
        .get(0, [])
    )

    if not handlers:
        raise RuntimeError(
            "Nenhum handler foi registrado."
        )

    conversation = handlers[0]

    if not isinstance(
        conversation,
        ConversationHandler,
    ):
        raise RuntimeError(
            (
                "O primeiro handler deve ser "
                "o ConversationHandler de despesas."
            )
        )

    if len(conversation.states) != 13:
        raise RuntimeError(
            (
                "Quantidade inesperada de estados: "
                f"{len(conversation.states)}."
            )
        )

    print(
        "[OK] ConversationHandler registrado."
    )
    print(
        (
            "[OK] Estados configurados: "
            f"{len(conversation.states)}."
        )
    )


if __name__ == "__main__":
    main()
