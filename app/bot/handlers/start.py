from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.bot.keyboards.main_menu import get_main_menu


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    text = (
        f"Olá, {user.first_name}!\n\n"
        "Bem-vindo ao FinanceBot.\n\n"
        "Escolha uma opção abaixo."
    )

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            get_main_menu(),
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True,
        ),
    )


async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text

    match text:

        case "💸 Novo gasto":
            await update.message.reply_text(
                "Função em desenvolvimento."
            )

        case "📋 Consultar gastos":
            await update.message.reply_text(
                "Função em desenvolvimento."
            )

        case "💰 Saldo":
            await update.message.reply_text(
                "Função em desenvolvimento."
            )

        case "📊 Relatórios":
            await update.message.reply_text(
                "Função em desenvolvimento."
            )

        case "⚙️ Configurações":
            await update.message.reply_text(
                "Função em desenvolvimento."
            )

        case _:
            await update.message.reply_text(
                "Opção inválida.\nEscolha uma opção do menu."
            )