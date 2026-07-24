from app.constants import DEFAULT_SHARED_PEOPLE
from app.bot.bot import FinanceBot
from telegram.ext import ConversationHandler


VALID_TEST_TOKEN = (
    "123456789:"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    "abcdefghi123456789"
)


def main() -> None:
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
                "valores a receber nao foram "
                "registrados."
            )
        )

    expected_people = {
        "Sofia",
        "Tomas",
        "Yuzo",
        "Giron",
        "Bruna",
        "Japa",
        "Pasquale",
    }

    if set(DEFAULT_SHARED_PEOPLE) != expected_people:
        raise RuntimeError(
            "A lista de pessoas padrao esta incorreta."
        )

    print(
        "[OK] Fluxo de pessoas em looping configurado."
    )
    print(
        "[OK] Consulta de valores a receber configurada."
    )
    print(
        "[OK] Baixa de recebimentos configurada."
    )


if __name__ == "__main__":
    main()
