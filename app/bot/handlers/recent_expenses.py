from telegram import Update
from telegram.ext import ContextTypes

from app.bot.expense_input import format_brl
from app.bot.keyboards.main_menu import (
    build_main_menu,
)
from app.container import container_context


RECENT_EXPENSE_LIMIT = 5


async def show_recent_expenses(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    message = update.effective_message

    if message is None:
        return

    with container_context() as container:
        expenses = (
            container.expense_query_service
            .list_recent(
                limit=RECENT_EXPENSE_LIMIT
            )
        )

    if not expenses:
        await message.reply_text(
            (
                "Nenhum lancamento cadastrado ainda."
            ),
            reply_markup=build_main_menu(),
        )
        return

    lines = [
        "\U0001f9fe Ultimos lancamentos",
        "",
    ]

    for index, expense in enumerate(
        expenses,
        start=1,
    ):
        markers = []

        if expense.is_installment:
            markers.append("parcelada")

        if expense.is_shared:
            markers.append("compartilhada")

        suffix = (
            " | " + ", ".join(markers)
            if markers
            else ""
        )

        lines.extend(
            [
                (
                    f"{index}. "
                    + expense.purchase_place
                ),
                (
                    "   "
                    + expense.purchase_date.strftime(
                        "%d/%m/%Y"
                    )
                    + " | "
                    + format_brl(
                        expense.purchase_value
                    )
                ),
                (
                    "   "
                    + expense.category_name
                    + " | "
                    + expense.payment_method_name
                    + suffix
                ),
                "",
            ]
        )

    lines.append(
        (
            "Mostrando os "
            f"{len(expenses)} mais recentes."
        )
    )

    await message.reply_text(
        "\n".join(lines),
        reply_markup=build_main_menu(),
    )
