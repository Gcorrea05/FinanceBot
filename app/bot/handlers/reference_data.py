from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards.main_menu import build_main_menu
from app.container import container_context


def format_reference_list(
    title: str,
    names: list[str],
) -> str:
    if not names:
        return (
            f"{title}\n\n"
            "Nenhum item cadastrado."
        )

    lines = [
        f"{index}. {name}"
        for index, name in enumerate(
            names,
            start=1,
        )
    ]

    return (
        f"{title}\n\n"
        + "\n".join(lines)
    )


async def list_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    with container_context() as container:
        names = (
            container.lookup_service
            .list_category_names()
        )

    await message.reply_text(
        text=format_reference_list(
            title="\U0001f4c2 Categorias disponiveis",
            names=names,
        ),
        reply_markup=build_main_menu(),
    )


async def list_payment_methods(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    with container_context() as container:
        names = (
            container.lookup_service
            .list_payment_method_names()
        )

    await message.reply_text(
        text=format_reference_list(
            title=(
                "\U0001f4b3 "
                "Formas de pagamento disponiveis"
            ),
            names=names,
        ),
        reply_markup=build_main_menu(),
    )
