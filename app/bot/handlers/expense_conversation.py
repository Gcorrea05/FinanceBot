import re
from datetime import date
from decimal import Decimal

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot.expense_input import (
    ExpenseInputError,
    format_brl,
    parse_date_input,
    parse_equal_people,
    parse_exact_people,
    parse_installment_count,
    parse_purchase_datetime,
    parse_shared_mode,
    parse_yes_no,
)
from app.bot.keyboards.expense import (
    BUTTON_BACK,
    BUTTON_CANCEL,
    BUTTON_CONFIRM,
    BUTTON_EXACT_SPLIT,
    BUTTON_RESTART,
    BUTTON_SKIP,
    build_choice_keyboard,
    build_confirmation_keyboard,
    build_date_keyboard,
    build_notes_keyboard,
    build_shared_mode_keyboard,
    build_yes_no_keyboard,
)
from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    build_main_menu,
)
from app.container import container_context
from app.domain.exceptions import DomainError
from app.domain.money import MoneyParser
from app.domain.shared_expense import (
    SharedExpenseSplitter,
)
from app.schemas.expense.create import ExpenseCreate
from app.services.lookup_service import (
    LookupNotFoundError,
)


(
    PURCHASE_DATE,
    PURCHASE_PLACE,
    PURCHASE_VALUE,
    CATEGORY,
    PAYMENT_METHOD,
    INSTALLMENT_CHOICE,
    INSTALLMENTS,
    FIRST_DUE_DATE,
    SHARED_CHOICE,
    SHARED_MODE,
    SHARED_PEOPLE,
    NOTES,
    CONFIRM,
) = range(13)


DRAFT_KEY = "expense_draft"
CURRENT_STATE_KEY = "expense_current_state"
HISTORY_KEY = "expense_state_history"


TEXT_FILTER = (
    filters.TEXT
    & ~filters.COMMAND
)

BACK_FILTER = filters.Regex(
    rf"^{re.escape(BUTTON_BACK)}$"
)

CANCEL_FILTER = filters.Regex(
    rf"^{re.escape(BUTTON_CANCEL)}$"
)


def _message(update: Update):
    return update.effective_message


def _draft(
    context: ContextTypes.DEFAULT_TYPE,
) -> dict:
    return context.user_data.setdefault(
        DRAFT_KEY,
        {},
    )


def _clear_flow(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    context.user_data.pop(
        DRAFT_KEY,
        None,
    )
    context.user_data.pop(
        CURRENT_STATE_KEY,
        None,
    )
    context.user_data.pop(
        HISTORY_KEY,
        None,
    )


def _move_to(
    context: ContextTypes.DEFAULT_TYPE,
    next_state: int,
) -> int:
    current_state = context.user_data.get(
        CURRENT_STATE_KEY
    )

    if current_state is not None:
        history = context.user_data.setdefault(
            HISTORY_KEY,
            [],
        )
        history.append(current_state)

    context.user_data[
        CURRENT_STATE_KEY
    ] = next_state

    return next_state


async def start_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear_flow(context)

    context.user_data[DRAFT_KEY] = {}
    context.user_data[HISTORY_KEY] = []
    context.user_data[
        CURRENT_STATE_KEY
    ] = PURCHASE_DATE

    message = _message(update)

    if message is None:
        return ConversationHandler.END

    await message.reply_text(
        (
            "Vamos cadastrar uma despesa.\n\n"
            "Qual foi a data da compra?\n"
            "Envie DD/MM/AAAA ou escolha Hoje."
        ),
        reply_markup=build_date_keyboard(),
    )

    return PURCHASE_DATE


async def receive_purchase_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return PURCHASE_DATE

    try:
        purchase_date = (
            parse_purchase_datetime(
                message.text or ""
            )
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error),
            reply_markup=build_date_keyboard(),
        )
        return PURCHASE_DATE

    if purchase_date.date() > date.today():
        await message.reply_text(
            "A data da compra nao pode estar no futuro.",
            reply_markup=build_date_keyboard(),
        )
        return PURCHASE_DATE

    _draft(context)[
        "purchase_date"
    ] = purchase_date

    await message.reply_text(
        "Em qual estabelecimento foi a compra?",
        reply_markup=build_choice_keyboard(
            [],
        ),
    )

    return _move_to(
        context,
        PURCHASE_PLACE,
    )


async def receive_purchase_place(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return PURCHASE_PLACE

    purchase_place = " ".join(
        (message.text or "").split()
    )

    if len(purchase_place) < 2:
        await message.reply_text(
            "Informe um estabelecimento com pelo menos 2 caracteres."
        )
        return PURCHASE_PLACE

    if len(purchase_place) > 255:
        await message.reply_text(
            "O estabelecimento deve possuir no maximo 255 caracteres."
        )
        return PURCHASE_PLACE

    _draft(context)[
        "purchase_place"
    ] = purchase_place

    await message.reply_text(
        (
            "Qual foi o valor total?\n"
            "Exemplos: 150,75 ou R$ 1.234,56."
        ),
        reply_markup=build_choice_keyboard(
            [],
        ),
    )

    return _move_to(
        context,
        PURCHASE_VALUE,
    )


async def receive_purchase_value(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return PURCHASE_VALUE

    try:
        purchase_value = MoneyParser.parse(
            message.text or ""
        )

    except ValueError as error:
        await message.reply_text(
            str(error)
        )
        return PURCHASE_VALUE

    _draft(context)[
        "purchase_value"
    ] = purchase_value

    await _prompt_category(
        message=message,
    )

    return _move_to(
        context,
        CATEGORY,
    )


async def receive_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return CATEGORY

    try:
        with container_context() as container:
            category = (
                container.lookup_service
                .get_category(
                    message.text or ""
                )
            )

    except LookupNotFoundError as error:
        await message.reply_text(
            str(error)
        )
        return CATEGORY

    _draft(context)[
        "category"
    ] = category.name

    await _prompt_payment_method(
        message=message,
    )

    return _move_to(
        context,
        PAYMENT_METHOD,
    )


async def receive_payment_method(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return PAYMENT_METHOD

    try:
        with container_context() as container:
            payment_method = (
                container.lookup_service
                .get_payment_method(
                    message.text or ""
                )
            )

    except LookupNotFoundError as error:
        await message.reply_text(
            str(error)
        )
        return PAYMENT_METHOD

    _draft(context)[
        "payment_method"
    ] = payment_method.name

    await message.reply_text(
        "A compra foi parcelada?",
        reply_markup=build_yes_no_keyboard(),
    )

    return _move_to(
        context,
        INSTALLMENT_CHOICE,
    )


async def receive_installment_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return INSTALLMENT_CHOICE

    try:
        is_installment = parse_yes_no(
            message.text or ""
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error),
            reply_markup=build_yes_no_keyboard(),
        )
        return INSTALLMENT_CHOICE

    draft = _draft(context)
    draft[
        "is_installment"
    ] = is_installment

    if not is_installment:
        draft["installments"] = 1
        draft[
            "first_installment_due_date"
        ] = None

        await message.reply_text(
            "A despesa foi compartilhada com alguem?",
            reply_markup=build_yes_no_keyboard(),
        )

        return _move_to(
            context,
            SHARED_CHOICE,
        )

    await message.reply_text(
        "Em quantas parcelas?",
        reply_markup=build_choice_keyboard(
            [
                "2",
                "3",
                "6",
                "10",
                "12",
            ],
            columns=3,
        ),
    )

    return _move_to(
        context,
        INSTALLMENTS,
    )


async def receive_installments(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return INSTALLMENTS

    try:
        installments = parse_installment_count(
            message.text or ""
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error)
        )
        return INSTALLMENTS

    _draft(context)[
        "installments"
    ] = installments

    await message.reply_text(
        (
            "Qual e a data de vencimento da primeira parcela?\n"
            "Envie DD/MM/AAAA ou escolha Data da compra."
        ),
        reply_markup=build_date_keyboard(
            allow_purchase_date=True,
            include_back=True,
        ),
    )

    return _move_to(
        context,
        FIRST_DUE_DATE,
    )


async def receive_first_due_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return FIRST_DUE_DATE

    draft = _draft(context)
    purchase_date = draft[
        "purchase_date"
    ].date()

    try:
        due_date = parse_date_input(
            message.text or "",
            purchase_date=purchase_date,
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error)
        )
        return FIRST_DUE_DATE

    if due_date < purchase_date:
        await message.reply_text(
            (
                "O primeiro vencimento nao pode ser "
                "anterior a data da compra."
            )
        )
        return FIRST_DUE_DATE

    draft[
        "first_installment_due_date"
    ] = due_date

    await message.reply_text(
        "A despesa foi compartilhada com alguem?",
        reply_markup=build_yes_no_keyboard(),
    )

    return _move_to(
        context,
        SHARED_CHOICE,
    )


async def receive_shared_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return SHARED_CHOICE

    try:
        is_shared = parse_yes_no(
            message.text or ""
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error),
            reply_markup=build_yes_no_keyboard(),
        )
        return SHARED_CHOICE

    draft = _draft(context)
    draft["is_shared"] = is_shared

    if not is_shared:
        draft["shared_mode"] = None
        draft["shared_people"] = ()

        await message.reply_text(
            (
                "Deseja adicionar uma observacao?\n"
                "Envie o texto ou escolha Pular."
            ),
            reply_markup=build_notes_keyboard(),
        )

        return _move_to(
            context,
            NOTES,
        )

    await message.reply_text(
        (
            "Como deseja dividir?\n\n"
            "Divisao igual: o valor e dividido entre "
            "voce e as pessoas informadas.\n"
            "Valores exatos: informe quanto cada pessoa deve."
        ),
        reply_markup=build_shared_mode_keyboard(),
    )

    return _move_to(
        context,
        SHARED_MODE,
    )


async def receive_shared_mode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return SHARED_MODE

    try:
        shared_mode = parse_shared_mode(
            message.text or ""
        )

    except ExpenseInputError as error:
        await message.reply_text(
            str(error),
            reply_markup=build_shared_mode_keyboard(),
        )
        return SHARED_MODE

    _draft(context)[
        "shared_mode"
    ] = shared_mode

    if shared_mode == "equal":
        prompt = (
            "Informe os nomes separados por virgula.\n"
            "Exemplo: Ana, Bruno"
        )
    else:
        prompt = (
            "Informe nome e valor, separados por ponto e virgula.\n"
            "Exemplo: Ana=30,00; Bruno=20,00"
        )

    await message.reply_text(
        prompt,
        reply_markup=build_choice_keyboard(
            [],
        ),
    )

    return _move_to(
        context,
        SHARED_PEOPLE,
    )


async def receive_shared_people(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return SHARED_PEOPLE

    draft = _draft(context)

    try:
        if draft["shared_mode"] == "equal":
            people = parse_equal_people(
                message.text or ""
            )
        else:
            people = parse_exact_people(
                message.text or ""
            )

        SharedExpenseSplitter().split(
            total=draft["purchase_value"],
            people=people,
        )

    except (
        ExpenseInputError,
        DomainError,
    ) as error:
        await message.reply_text(
            str(error)
        )
        return SHARED_PEOPLE

    draft[
        "shared_people"
    ] = people

    await message.reply_text(
        (
            "Deseja adicionar uma observacao?\n"
            "Envie o texto ou escolha Pular."
        ),
        reply_markup=build_notes_keyboard(),
    )

    return _move_to(
        context,
        NOTES,
    )


async def receive_notes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return NOTES

    raw_notes = (
        message.text or ""
    ).strip()

    if raw_notes == BUTTON_SKIP:
        notes = None
    else:
        notes = " ".join(
            raw_notes.split()
        )

        if len(notes) > 500:
            await message.reply_text(
                "A observacao deve possuir no maximo 500 caracteres."
            )
            return NOTES

        if not notes:
            notes = None

    _draft(context)["notes"] = notes

    context.user_data[
        CURRENT_STATE_KEY
    ] = CONFIRM
    context.user_data.setdefault(
        HISTORY_KEY,
        [],
    ).append(NOTES)

    await _show_review(
        message=message,
        context=context,
    )

    return CONFIRM


async def confirm_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = _message(update)

    if message is None:
        return CONFIRM

    action = (
        message.text or ""
    ).strip()

    if action == BUTTON_RESTART:
        return await start_expense(
            update,
            context,
        )

    if action != BUTTON_CONFIRM:
        await message.reply_text(
            "Escolha Confirmar, Recomecar, Voltar ou Cancelar.",
            reply_markup=build_confirmation_keyboard(),
        )
        return CONFIRM

    draft = _draft(context)

    data = ExpenseCreate(
        purchase_date=draft["purchase_date"],
        purchase_place=draft["purchase_place"],
        purchase_value=draft["purchase_value"],
        category=draft["category"],
        payment_method=draft["payment_method"],
        is_installment=draft["is_installment"],
        installments=draft["installments"],
        first_installment_due_date=(
            draft[
                "first_installment_due_date"
            ]
        ),
        is_shared=draft["is_shared"],
        shared_people=tuple(
            draft["shared_people"]
        ),
        notes=draft.get("notes"),
    )

    try:
        with container_context() as container:
            expense = (
                container.expense_service
                .create_expense(data)
            )

    except (
        DomainError,
        LookupNotFoundError,
        ValueError,
    ) as error:
        await message.reply_text(
            (
                "Nao foi possivel salvar a despesa:\n"
                f"{error}\n\n"
                "Use Voltar para corrigir ou Cancelar."
            ),
            reply_markup=build_confirmation_keyboard(),
        )
        return CONFIRM

    expense_id = getattr(
        expense,
        "id",
        None,
    )

    suffix = (
        f" #{expense_id}"
        if expense_id is not None
        else ""
    )

    _clear_flow(context)

    await message.reply_text(
        (
            f"Despesa{suffix} cadastrada com sucesso."
        ),
        reply_markup=build_main_menu(),
    )

    return ConversationHandler.END


async def go_back(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    history = context.user_data.get(
        HISTORY_KEY,
        [],
    )

    if not history:
        return await cancel_expense(
            update,
            context,
        )

    previous_state = history.pop()
    context.user_data[
        CURRENT_STATE_KEY
    ] = previous_state

    message = _message(update)

    if message is None:
        return previous_state

    await _prompt_state(
        message=message,
        context=context,
        state=previous_state,
    )

    return previous_state


async def cancel_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear_flow(context)

    message = _message(update)

    if message is not None:
        await message.reply_text(
            "Cadastro de despesa cancelado.",
            reply_markup=build_main_menu(),
        )

    return ConversationHandler.END


async def cancel_to_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear_flow(context)

    message = _message(update)

    if message is not None:
        await message.reply_text(
            (
                "FinanceBot\n\n"
                "Escolha uma opcao no menu."
            ),
            reply_markup=build_main_menu(),
        )

    return ConversationHandler.END


async def _prompt_state(
    *,
    message,
    context: ContextTypes.DEFAULT_TYPE,
    state: int,
) -> None:
    if state == PURCHASE_DATE:
        await message.reply_text(
            (
                "Qual foi a data da compra?\n"
                "Envie DD/MM/AAAA ou escolha Hoje."
            ),
            reply_markup=build_date_keyboard(),
        )
        return

    if state == PURCHASE_PLACE:
        await message.reply_text(
            "Em qual estabelecimento foi a compra?",
            reply_markup=build_choice_keyboard(
                [],
            ),
        )
        return

    if state == PURCHASE_VALUE:
        await message.reply_text(
            "Qual foi o valor total?",
            reply_markup=build_choice_keyboard(
                [],
            ),
        )
        return

    if state == CATEGORY:
        await _prompt_category(
            message=message,
        )
        return

    if state == PAYMENT_METHOD:
        await _prompt_payment_method(
            message=message,
        )
        return

    if state == INSTALLMENT_CHOICE:
        await message.reply_text(
            "A compra foi parcelada?",
            reply_markup=build_yes_no_keyboard(),
        )
        return

    if state == INSTALLMENTS:
        await message.reply_text(
            "Em quantas parcelas?",
            reply_markup=build_choice_keyboard(
                [
                    "2",
                    "3",
                    "6",
                    "10",
                    "12",
                ],
                columns=3,
            ),
        )
        return

    if state == FIRST_DUE_DATE:
        await message.reply_text(
            (
                "Qual e a data de vencimento "
                "da primeira parcela?"
            ),
            reply_markup=build_date_keyboard(
                allow_purchase_date=True,
                include_back=True,
            ),
        )
        return

    if state == SHARED_CHOICE:
        await message.reply_text(
            "A despesa foi compartilhada com alguem?",
            reply_markup=build_yes_no_keyboard(),
        )
        return

    if state == SHARED_MODE:
        await message.reply_text(
            "Como deseja dividir?",
            reply_markup=build_shared_mode_keyboard(),
        )
        return

    if state == SHARED_PEOPLE:
        shared_mode = _draft(
            context
        ).get("shared_mode")

        example = (
            "Ana, Bruno"
            if shared_mode == "equal"
            else "Ana=30,00; Bruno=20,00"
        )

        await message.reply_text(
            f"Informe as pessoas. Exemplo: {example}",
            reply_markup=build_choice_keyboard(
                [],
            ),
        )
        return

    if state == NOTES:
        await message.reply_text(
            "Envie uma observacao ou escolha Pular.",
            reply_markup=build_notes_keyboard(),
        )
        return

    if state == CONFIRM:
        await _show_review(
            message=message,
            context=context,
        )


async def _prompt_category(
    *,
    message,
) -> None:
    with container_context() as container:
        names = (
            container.lookup_service
            .list_category_names()
        )

    await message.reply_text(
        "Escolha ou digite a categoria:",
        reply_markup=build_choice_keyboard(
            names,
            columns=2,
        ),
    )


async def _prompt_payment_method(
    *,
    message,
) -> None:
    with container_context() as container:
        names = (
            container.lookup_service
            .list_payment_method_names()
        )

    await message.reply_text(
        "Escolha ou digite a forma de pagamento:",
        reply_markup=build_choice_keyboard(
            names,
            columns=2,
        ),
    )


async def _show_review(
    *,
    message,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    draft = _draft(context)

    lines = [
        "Revise a despesa:",
        "",
        (
            "Data: "
            + draft["purchase_date"].strftime(
                "%d/%m/%Y"
            )
        ),
        (
            "Estabelecimento: "
            + draft["purchase_place"]
        ),
        (
            "Valor: "
            + format_brl(
                draft["purchase_value"]
            )
        ),
        (
            "Categoria: "
            + draft["category"]
        ),
        (
            "Pagamento: "
            + draft["payment_method"]
        ),
    ]

    if draft["is_installment"]:
        lines.append(
            (
                "Parcelamento: "
                f"{draft['installments']}x"
            )
        )
        lines.append(
            (
                "Primeiro vencimento: "
                + draft[
                    "first_installment_due_date"
                ].strftime("%d/%m/%Y")
            )
        )
    else:
        lines.append(
            "Parcelamento: nao"
        )

    if draft["is_shared"]:
        split = SharedExpenseSplitter().split(
            total=draft["purchase_value"],
            people=tuple(
                draft["shared_people"]
            ),
        )

        lines.append(
            (
                "Sua parte: "
                + format_brl(
                    split.owner_amount
                )
            )
        )

        lines.append(
            "Pessoas:"
        )

        for allocation in split.allocations:
            lines.append(
                (
                    f"- {allocation.person_name}: "
                    + format_brl(
                        allocation.amount
                    )
                )
            )
    else:
        lines.append(
            "Compartilhada: nao"
        )

    lines.append(
        (
            "Observacao: "
            + (
                draft.get("notes")
                or "-"
            )
        )
    )

    lines.extend(
        [
            "",
            "Confirma o cadastro?",
        ]
    )

    await message.reply_text(
        "\n".join(lines),
        reply_markup=build_confirmation_keyboard(),
    )


def build_expense_conversation_handler(
) -> ConversationHandler:
    state_handlers = {
        PURCHASE_DATE: receive_purchase_date,
        PURCHASE_PLACE: receive_purchase_place,
        PURCHASE_VALUE: receive_purchase_value,
        CATEGORY: receive_category,
        PAYMENT_METHOD: receive_payment_method,
        INSTALLMENT_CHOICE: (
            receive_installment_choice
        ),
        INSTALLMENTS: receive_installments,
        FIRST_DUE_DATE: receive_first_due_date,
        SHARED_CHOICE: receive_shared_choice,
        SHARED_MODE: receive_shared_mode,
        SHARED_PEOPLE: receive_shared_people,
        NOTES: receive_notes,
        CONFIRM: confirm_expense,
    }

    states = {
        state: [
            MessageHandler(
                BACK_FILTER,
                go_back,
            ),
            MessageHandler(
                CANCEL_FILTER,
                cancel_expense,
            ),
            MessageHandler(
                TEXT_FILTER,
                callback,
            ),
        ]
        for state, callback in state_handlers.items()
    }

    return ConversationHandler(
        entry_points=[
            CommandHandler(
                "gasto",
                start_expense,
            ),
            MessageHandler(
                filters.Regex(
                    (
                        "^"
                        + re.escape(
                            MENU_ADD_EXPENSE
                        )
                        + "$"
                    )
                ),
                start_expense,
            ),
        ],
        states=states,
        fallbacks=[
            CommandHandler(
                "cancelar",
                cancel_expense,
            ),
            CommandHandler(
                "start",
                cancel_to_menu,
            ),
            MessageHandler(
                CANCEL_FILTER,
                cancel_expense,
            ),
        ],
        allow_reentry=True,
        per_chat=True,
        per_user=True,
        per_message=False,
    )
