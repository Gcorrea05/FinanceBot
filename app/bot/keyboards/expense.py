from collections.abc import Sequence

from telegram import ReplyKeyboardMarkup


BUTTON_TODAY = "Hoje"
BUTTON_PURCHASE_DATE = "Data da compra"
BUTTON_YES = "Sim"
BUTTON_NO = "Nao"
BUTTON_BACK = "Voltar"
BUTTON_CANCEL = "Cancelar"
BUTTON_SKIP = "Pular"
BUTTON_CONFIRM = "Confirmar"
BUTTON_RESTART = "Recomecar"
BUTTON_EQUAL_SPLIT = "Divisao igual"
BUTTON_EXACT_SPLIT = "Valores exatos"


def build_choice_keyboard(
    options: Sequence[str],
    *,
    columns: int = 2,
    include_back: bool = True,
) -> ReplyKeyboardMarkup:
    rows = [
        list(
            options[index:index + columns]
        )
        for index in range(
            0,
            len(options),
            columns,
        )
    ]

    navigation: list[str] = []

    if include_back:
        navigation.append(BUTTON_BACK)

    navigation.append(BUTTON_CANCEL)
    rows.append(navigation)

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def build_date_keyboard(
    *,
    allow_purchase_date: bool = False,
    include_back: bool = False,
) -> ReplyKeyboardMarkup:
    options = [BUTTON_TODAY]

    if allow_purchase_date:
        options.append(
            BUTTON_PURCHASE_DATE
        )

    return build_choice_keyboard(
        options,
        columns=2,
        include_back=include_back,
    )


def build_yes_no_keyboard() -> ReplyKeyboardMarkup:
    return build_choice_keyboard(
        [
            BUTTON_YES,
            BUTTON_NO,
        ],
    )


def build_shared_mode_keyboard() -> ReplyKeyboardMarkup:
    return build_choice_keyboard(
        [
            BUTTON_EQUAL_SPLIT,
            BUTTON_EXACT_SPLIT,
        ],
        columns=1,
    )


def build_notes_keyboard() -> ReplyKeyboardMarkup:
    return build_choice_keyboard(
        [BUTTON_SKIP],
        columns=1,
    )


def build_confirmation_keyboard() -> ReplyKeyboardMarkup:
    return build_choice_keyboard(
        [
            BUTTON_CONFIRM,
            BUTTON_RESTART,
        ],
        columns=1,
        include_back=True,
    )
