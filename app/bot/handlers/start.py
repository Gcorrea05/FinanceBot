from telegram import Update
from telegram.ext import ContextTypes

from app.container import container_context
from app.bot.handlers.expense_conversation import (
    start_expense,
)
from app.bot.handlers.receivables import (
    start_receivables,
)
from app.bot.handlers.recent_expenses import (
    show_recent_expenses,
)
from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    MENU_HELP,
    MENU_RECEIVABLES,
    MENU_RECENT_EXPENSES,
    build_main_menu,
)


WELCOME_TEXT = (
    "\U0001f4b0 FinanceBot\n\n"
    "Registre despesas e faca consultas rapidas."
)


HELP_TEXT = (
    "\u2753 Comandos disponiveis\n\n"
    "/start - abrir o menu principal\n"
    "/gasto - cadastrar uma despesa\n"
    "/ultimos - ver os ultimos lancamentos\n"
    "/receber - consultar valores a receber\n"
    "/cancelar - cancelar o fluxo atual\n"
    "/notificacoes - vincular este chat aos alertas\n"
    "/ajuda - exibir esta ajuda"
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )


async def link_notifications(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message
    chat = update.effective_chat

    if (
        message is None
        or chat is None
    ):
        return

    with container_context() as container:
        container.automation_service.link_telegram_chat(
            chat.id
        )

    await message.reply_text(
        text=(
            "Este chat foi vinculado "
            "as notificacoes automaticas."
        ),
        reply_markup=build_main_menu(),
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=HELP_TEXT,
        reply_markup=build_main_menu(),
    )


async def unknown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=(
            "Comando nao reconhecido. "
            "Use /ajuda."
        ),
        reply_markup=build_main_menu(),
    )


async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None:
        return

    text = (message.text or "").strip()

    if text == MENU_ADD_EXPENSE:
        await start_expense(
            update,
            context,
        )
        return

    if text == MENU_RECENT_EXPENSES:
        await show_recent_expenses(
            update,
            context,
        )
        return

    if text == MENU_RECEIVABLES:
        await start_receivables(
            update,
            context,
        )
        return

    if text == MENU_HELP:
        await help_command(
            update,
            context,
        )
        return

    await message.reply_text(
        text=(
            "Nao reconheci essa opcao. "
            "Escolha um item do menu."
        ),
        reply_markup=build_main_menu(),
    )
