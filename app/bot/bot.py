from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers.start import start
from app.bot.handlers.start import menu_handler
from app.config import settings


class FinanceBot:

    def __init__(self):

        self.application = (
            Application.builder()
            .token(settings.TELEGRAM_TOKEN)
            .build()
        )

        self.register_handlers()

    def register_handlers(self):

        self.application.add_handler(
            CommandHandler("start", start)
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                menu_handler,
            )
        )

    def run(self):

        print("FinanceBot iniciado.")

        self.application.run_polling()