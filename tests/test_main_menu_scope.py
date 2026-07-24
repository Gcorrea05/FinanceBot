from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    MENU_HELP,
    MENU_RECEIVABLES,
    MENU_RECENT_EXPENSES,
    build_main_menu,
)


def _button_text(button) -> str:
    return getattr(
        button,
        "text",
        str(button),
    )


def test_main_menu_contains_only_operational_actions():
    menu = build_main_menu()

    labels = [
        _button_text(button)
        for row in menu.keyboard
        for button in row
    ]

    assert labels == [
        MENU_ADD_EXPENSE,
        MENU_RECENT_EXPENSES,
        MENU_RECEIVABLES,
        MENU_HELP,
    ]

    combined = " ".join(labels).casefold()

    assert "categoria" not in combined
    assert "pagamento" not in combined
    assert "relatorio" not in combined
    assert "saldo" not in combined


def test_main_menu_is_persistent():
    menu = build_main_menu()

    assert menu.resize_keyboard is True
    assert menu.one_time_keyboard is False
    assert menu.is_persistent is True
