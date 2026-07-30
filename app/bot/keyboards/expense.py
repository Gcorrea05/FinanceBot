from telegram import ReplyKeyboardMarkup

PAYMENT_CREDIT_CARD = "Cartão de crédito"
PAYMENT_DEBIT = "Débito"
PAYMENT_PIX = "Pix"
PAYMENT_CASH = "Dinheiro"
PAYMENT_METHODS = (
    PAYMENT_CREDIT_CARD,
    PAYMENT_DEBIT,
    PAYMENT_PIX,
    PAYMENT_CASH,
)

BUTTON_CONFIRM = "Confirmar"
BUTTON_CANCEL = "Cancelar"


def build_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [PAYMENT_CREDIT_CARD, PAYMENT_DEBIT],
            [PAYMENT_PIX, PAYMENT_CASH],
            [BUTTON_CANCEL],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def build_confirmation_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[BUTTON_CONFIRM, BUTTON_CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
