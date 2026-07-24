from telegram import ReplyKeyboardMarkup


MENU_ADD_EXPENSE = "\u2795 Adicionar gasto"
MENU_RECEIVABLES = "\U0001f4b0 Valores a receber"
MENU_CATEGORIES = "\U0001f4c2 Categorias"
MENU_PAYMENT_METHODS = "\U0001f4b3 Formas de pagamento"
MENU_HELP = "\u2753 Ajuda"


def build_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [MENU_ADD_EXPENSE],
            [MENU_RECEIVABLES],
            [
                MENU_CATEGORIES,
                MENU_PAYMENT_METHODS,
            ],
            [MENU_HELP],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )
