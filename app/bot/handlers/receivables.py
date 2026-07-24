import re
from decimal import Decimal

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot.expense_input import format_brl
from app.bot.keyboards.main_menu import (
    MENU_RECEIVABLES,
    build_main_menu,
)
from app.bot.keyboards.receivables import (
    BUTTON_BACK_TO_MENU,
    BUTTON_BACK_TO_SUMMARY,
    BUTTON_CANCEL_RECEIPT,
    BUTTON_CONFIRM_RECEIPT,
    build_items_keyboard,
    build_people_keyboard,
    build_receipt_confirmation_keyboard,
)
from app.container import container_context
from app.services.receivable_service import (
    ReceivableNotFoundError,
)


(
    RECEIVABLE_PERSON,
    RECEIVABLE_ITEM,
    RECEIVABLE_CONFIRM,
) = range(3)


SUMMARY_KEY = "receivable_summary"
ITEMS_KEY = "receivable_items"
PERSON_KEY = "receivable_person"
SELECTED_KEY = "receivable_selected"


def _message(update: Update):
    return update.effective_message


def _clear_receivable_flow(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    for key in (
        SUMMARY_KEY,
        ITEMS_KEY,
        PERSON_KEY,
        SELECTED_KEY,
    ):
        context.user_data.pop(
            key,
            None,
        )


async def start_receivables(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear_receivable_flow(context)

    message = _message(update)

    if message is None:
        return ConversationHandler.END

    with container_context() as container:
        summary = (
            container.receivable_service
            .list_open_summary()
        )

    if not summary:
        await message.reply_text(
            "Nao existem valores pendentes a receber.",
            reply_markup=build_main_menu(),
        )
        return ConversationHandler.END

    context.user_data[SUMMARY_KEY] = [
        {
            "person_id": item.person_id,
            "person_name": item.person_name,
            "total": str(item.total),
            "pending_count": item.pending_count,
        }
        for item in summary
    ]

    requested_name = " ".join(
        getattr(context, "args", []) or []
    ).strip()

    if requested_name:
        return await _show_person_details(
            message=message,
            context=context,
            person_name=requested_name,
        )

    total = sum(
        (
            item.total
            for item in summary
        ),
        start=Decimal("0.00"),
    )

    lines = [
        "\U0001f4b0 Valores a receber",
        "",
    ]

    for item in summary:
        pending_label = (
            "pendencia"
            if item.pending_count == 1
            else "pendencias"
        )

        lines.append(
            (
                f"{item.person_name} - "
                f"{format_brl(item.total)} - "
                f"{item.pending_count} "
                f"{pending_label}"
            )
        )

    lines.extend(
        [
            "",
            (
                "Total geral: "
                + format_brl(total)
            ),
            "",
            (
                "Escolha uma pessoa para "
                "ver os detalhes."
            ),
        ]
    )

    await message.reply_text(
        "\n".join(lines),
        reply_markup=build_people_keyboard(
            [
                item.person_name
                for item in summary
            ]
        ),
    )

    return RECEIVABLE_PERSON


async def select_receivable_person(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return RECEIVABLE_PERSON

    action = (message.text or "").strip()

    if action == BUTTON_BACK_TO_MENU:
        return await receivables_to_menu(
            update,
            context,
        )

    return await _show_person_details(
        message=message,
        context=context,
        person_name=action,
    )


async def _show_person_details(
    *,
    message,
    context: ContextTypes.DEFAULT_TYPE,
    person_name: str,
) -> int:
    try:
        with container_context() as container:
            items = (
                container.receivable_service
                .list_open_for_person_name(
                    person_name
                )
            )

    except ReceivableNotFoundError as error:
        await message.reply_text(
            str(error)
        )
        return RECEIVABLE_PERSON

    if not items:
        await message.reply_text(
            (
                f"Nao existem pendencias abertas "
                f"para {person_name}."
            ),
            reply_markup=build_main_menu(),
        )
        _clear_receivable_flow(context)
        return ConversationHandler.END

    context.user_data[PERSON_KEY] = {
        "person_id": items[0].person_id,
        "person_name": items[0].person_name,
    }

    context.user_data[ITEMS_KEY] = [
        {
            "receivable_id": item.receivable_id,
            "expense_id": item.expense_id,
            "person_id": item.person_id,
            "person_name": item.person_name,
            "purchase_place": item.purchase_place,
            "purchase_date": (
                item.purchase_date.isoformat()
            ),
            "amount": str(item.amount),
        }
        for item in items
    ]

    total = sum(
        (
            item.amount
            for item in items
        ),
        start=Decimal("0.00"),
    )

    lines = [
        (
            "\U0001f4b0 Pendencias de "
            + items[0].person_name
        ),
        "",
    ]

    for index, item in enumerate(
        items,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{index}. "
                    f"{item.purchase_place}"
                ),
                (
                    "   Data: "
                    + item.purchase_date.strftime(
                        "%d/%m/%Y"
                    )
                ),
                (
                    "   Valor: "
                    + format_brl(
                        item.amount
                    )
                ),
                "",
            ]
        )

    lines.extend(
        [
            (
                "Total de "
                f"{items[0].person_name}: "
                + format_brl(total)
            ),
            "",
            (
                "Escolha o numero de uma "
                "pendencia para marcar como recebida."
            ),
        ]
    )

    await message.reply_text(
        "\n".join(lines),
        reply_markup=build_items_keyboard(
            len(items)
        ),
    )

    return RECEIVABLE_ITEM


async def select_receivable_item(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return RECEIVABLE_ITEM

    action = (message.text or "").strip()

    if action == BUTTON_BACK_TO_SUMMARY:
        return await start_receivables(
            update,
            context,
        )

    if action == BUTTON_BACK_TO_MENU:
        return await receivables_to_menu(
            update,
            context,
        )

    try:
        selected_index = int(action) - 1

    except ValueError:
        selected_index = -1

    items = context.user_data.get(
        ITEMS_KEY,
        [],
    )

    if not 0 <= selected_index < len(items):
        await message.reply_text(
            "Escolha um numero valido da lista.",
            reply_markup=build_items_keyboard(
                len(items)
            ),
        )
        return RECEIVABLE_ITEM

    selected = items[selected_index]
    context.user_data[SELECTED_KEY] = selected

    await message.reply_text(
        (
            "Confirmar recebimento de "
            + format_brl(
                Decimal(
                    selected["amount"]
                )
            )
            + " de "
            + selected["person_name"]
            + "?"
        ),
        reply_markup=(
            build_receipt_confirmation_keyboard()
        ),
    )

    return RECEIVABLE_CONFIRM


async def confirm_receivable_settlement(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return RECEIVABLE_CONFIRM

    action = (message.text or "").strip()

    if action == BUTTON_BACK_TO_SUMMARY:
        person = context.user_data.get(
            PERSON_KEY,
            {},
        )

        return await _show_person_details(
            message=message,
            context=context,
            person_name=person.get(
                "person_name",
                "",
            ),
        )

    if action in {
        BUTTON_CANCEL_RECEIPT,
        BUTTON_BACK_TO_MENU,
    }:
        return await receivables_to_menu(
            update,
            context,
        )

    if action != BUTTON_CONFIRM_RECEIPT:
        await message.reply_text(
            "Escolha Confirmar recebimento ou Cancelar.",
            reply_markup=(
                build_receipt_confirmation_keyboard()
            ),
        )
        return RECEIVABLE_CONFIRM

    selected = context.user_data.get(
        SELECTED_KEY
    )

    if selected is None:
        await message.reply_text(
            "A pendencia selecionada nao esta mais disponivel."
        )
        return await start_receivables(
            update,
            context,
        )

    try:
        with container_context() as container:
            container.receivable_service.settle(
                selected["receivable_id"]
            )

    except ReceivableNotFoundError as error:
        await message.reply_text(
            str(error)
        )
        return await start_receivables(
            update,
            context,
        )

    await message.reply_text(
        (
            "Recebimento registrado: "
            + format_brl(
                Decimal(
                    selected["amount"]
                )
            )
            + " de "
            + selected["person_name"]
            + "."
        )
    )

    return await start_receivables(
        update,
        context,
    )


async def cancel_receivables(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    return await receivables_to_menu(
        update,
        context,
    )


async def receivables_to_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear_receivable_flow(context)

    message = _message(update)

    if message is not None:
        await message.reply_text(
            "FinanceBot",
            reply_markup=build_main_menu(),
        )

    return ConversationHandler.END


def build_receivables_conversation_handler(
) -> ConversationHandler:
    text_filter = (
        filters.TEXT
        & ~filters.COMMAND
    )

    return ConversationHandler(
        entry_points=[
            CommandHandler(
                "receber",
                start_receivables,
            ),
            MessageHandler(
                filters.Regex(
                    (
                        "^"
                        + re.escape(
                            MENU_RECEIVABLES
                        )
                        + "$"
                    )
                ),
                start_receivables,
            ),
        ],
        states={
            RECEIVABLE_PERSON: [
                MessageHandler(
                    text_filter,
                    select_receivable_person,
                )
            ],
            RECEIVABLE_ITEM: [
                MessageHandler(
                    text_filter,
                    select_receivable_item,
                )
            ],
            RECEIVABLE_CONFIRM: [
                MessageHandler(
                    text_filter,
                    confirm_receivable_settlement,
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancelar",
                cancel_receivables,
            ),
            CommandHandler(
                "start",
                receivables_to_menu,
            ),
        ],
        allow_reentry=True,
        per_chat=True,
        per_user=True,
        per_message=False,
    )
