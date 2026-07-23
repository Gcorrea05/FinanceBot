from telegram import KeyboardButton


def get_main_menu() -> list[list[KeyboardButton]]:
    """
    Retorna o teclado principal do FinanceBot.
    """

    return [
        [
            KeyboardButton("💸 Novo gasto"),
            KeyboardButton("💰 Saldo"),
        ],
        [
            KeyboardButton("📋 Consultar gastos"),
            KeyboardButton("📊 Relatórios"),
        ],
        [
            KeyboardButton("⚙️ Configurações"),
        ],
    ]