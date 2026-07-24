import logging

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers.error import error_handler
from app.bot.handlers.expense_conversation import (
    build_expense_conversation_handler,
)
from app.bot.handlers.receivables import (
    build_receivables_conversation_handler,
)
from app.bot.handlers.reference_data import (
    list_categories,
    list_payment_methods,
)
from app.bot.handlers.start import (
    help_command,
    menu_handler,
    start,
    unknown_command,
)
from app.config import settings


logger = logging.getLogger(__name__)


class FinanceBot:
    def __init__(
        self,
        token: str | None = None,
    ):
        if token is None:
            resolved_token = (
                settings.require_telegram_token()
            )
        else:
            resolved_token = token.strip()

        if not resolved_token:
            raise ValueError(
                "O token do Telegram nao pode ficar vazio."
            )

        self.application = (
            Application.builder()
            .token(resolved_token)
            .post_init(self._post_init)
            .build()
        )

        self.register_handlers()

    @staticmethod
    async def _post_init(
        application: Application,
    ) -> None:
        await application.bot.set_my_commands(
            commands=[
                BotCommand(
                    command="start",
                    description="Abrir o menu principal",
                ),
                BotCommand(
                    command="gasto",
                    description="Cadastrar uma despesa",
                ),
                BotCommand(
                    command="cancelar",
                    description="Cancelar o cadastro atual",
                ),
                BotCommand(
                    command="categorias",
                    description="Listar categorias",
                ),
                BotCommand(
                    command="pagamentos",
                    description=(
                        "Listar formas de pagamento"
                    ),
                ),
                BotCommand(
                    command="receber",
                    description="Consultar valores a receber",
                ),
                BotCommand(
                    command="ajuda",
                    description="Exibir ajuda",
                ),
            ]
        )

    def register_handlers(self) -> None:
        self.application.add_handler(
            build_receivables_conversation_handler()
        )

        self.application.add_handler(
            build_expense_conversation_handler()
        )

        self.application.add_handler(
            CommandHandler(
                command="start",
                callback=start,
            )
        )

        self.application.add_handler(
            CommandHandler(
                command="categorias",
                callback=list_categories,
            )
        )

        self.application.add_handler(
            CommandHandler(
                command="pagamentos",
                callback=list_payment_methods,
            )
        )

        self.application.add_handler(
            CommandHandler(
                command="ajuda",
                callback=help_command,
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters=filters.COMMAND,
                callback=unknown_command,
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters=(
                    filters.TEXT
                    & ~filters.COMMAND
                ),
                callback=menu_handler,
            )
        )

        self.application.add_error_handler(
            callback=error_handler
        )

    def run(self) -> None:
        logger.info(
            "FinanceBot iniciado."
        )

        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
