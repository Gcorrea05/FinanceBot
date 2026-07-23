from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.reference_data import (
    list_categories,
    list_payment_methods,
)
from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    MENU_CATEGORIES,
    MENU_HELP,
    MENU_PAYMENT_METHODS,
    build_main_menu,
)


WELCOME_TEXT = (
    "\U0001f4b0 FinanceBot\n\n"
    "Use o menu para cadastrar e consultar despesas."
)


HELP_TEXT = (
    "\u2753 Comandos disponiveis\n\n"
    "/start - abrir o menu principal\n"
    "/gasto - cadastrar uma despesa\n"
    "/cancelar - cancelar o cadastro atual\n"
    "/categorias - listar categorias\n"
    "/pagamentos - listar formas de pagamento\n"
    "/ajuda - exibir esta ajuda"
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=WELCOME_TEXT,
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


async def add_expense_placeholder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        text=(
            "Use /gasto ou o botao Adicionar gasto "
            "para iniciar o cadastro."
        ),
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

    if text == MENU_CATEGORIES:
        await list_categories(
            update,
            context,
        )
        return

    if text == MENU_PAYMENT_METHODS:
        await list_payment_methods(
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

    if text == MENU_ADD_EXPENSE:
        await add_expense_placeholder(
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
