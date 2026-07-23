import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards.main_menu import build_main_menu


logger = logging.getLogger(__name__)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.error(
        "Erro nao tratado pelo bot: %s",
        context.error,
    )

    if not isinstance(update, Update):
        return

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=(
            "Ocorreu um erro inesperado. "
            "Tente novamente."
        ),
        reply_markup=build_main_menu(),
    )
