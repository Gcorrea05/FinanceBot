from collections.abc import Sequence

from telegram import ReplyKeyboardMarkup


BUTTON_BACK_TO_SUMMARY = "Voltar ao resumo"
BUTTON_BACK_TO_MENU = "Voltar ao menu"
BUTTON_CONFIRM_RECEIPT = "Confirmar recebimento"
BUTTON_CANCEL_RECEIPT = "Cancelar"


def build_people_keyboard(
    names: Sequence[str],
) -> ReplyKeyboardMarkup:
    rows = [
        list(
            names[index:index + 2]
        )
        for index in range(
            0,
            len(names),
            2,
        )
    ]

    rows.append(
        [BUTTON_BACK_TO_MENU]
    )

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def build_items_keyboard(
    item_count: int,
) -> ReplyKeyboardMarkup:
    labels = [
        str(index)
        for index in range(
            1,
            item_count + 1,
        )
    ]

    rows = [
        labels[index:index + 4]
        for index in range(
            0,
            len(labels),
            4,
        )
    ]

    rows.append(
        [
            BUTTON_BACK_TO_SUMMARY,
            BUTTON_BACK_TO_MENU,
        ]
    )

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def build_receipt_confirmation_keyboard(
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [BUTTON_CONFIRM_RECEIPT],
            [
                BUTTON_BACK_TO_SUMMARY,
                BUTTON_CANCEL_RECEIPT,
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
