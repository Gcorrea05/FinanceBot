from telegram import ReplyKeyboardMarkup


MENU_ADD_EXPENSE = "\u2795 Adicionar gasto"
MENU_RECENT_EXPENSES = "\U0001f9fe Ultimos lancamentos"
MENU_RECEIVABLES = "\U0001f4b0 Valores a receber"
MENU_HELP = "\u2753 Ajuda"


def build_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [MENU_ADD_EXPENSE],
            [MENU_RECENT_EXPENSES],
            [MENU_RECEIVABLES],
            [MENU_HELP],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )
