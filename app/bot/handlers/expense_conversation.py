import re
from datetime import date, datetime
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
from app.bot.keyboards.expense import (
    BUTTON_CANCEL,
    BUTTON_CONFIRM,
    PAYMENT_CREDIT_CARD,
    PAYMENT_METHODS,
    build_confirmation_keyboard,
    build_payment_keyboard,
)
from app.bot.keyboards.main_menu import (
    MENU_ADD_EXPENSE,
    MENU_HELP,
    MENU_RECEIVABLES,
    MENU_RECENT_EXPENSES,
    build_main_menu,
)
from app.container import container_context
from app.domain.billing_cycle import first_installment_date
from app.domain.natural_expense_parser import (
    NaturalExpenseDraft,
    NaturalExpenseParseError,
    NaturalExpenseParser,
)
from app.domain.shared_expense import SharedExpenseSplitter
from app.schemas.expense.create import ExpenseCreate

NATURAL_TEXT, PAYMENT_METHOD, CONFIRM = range(3)
DRAFT_KEY = "natural_expense_draft"
PAYMENT_KEY = "natural_expense_payment"

_MENU_PATTERN = "^(?:" + "|".join(
    re.escape(value)
    for value in (
        MENU_ADD_EXPENSE,
        MENU_RECENT_EXPENSES,
        MENU_RECEIVABLES,
        MENU_HELP,
        *PAYMENT_METHODS,
        BUTTON_CONFIRM,
        BUTTON_CANCEL,
    )
) + ")$"

DIRECT_TEXT_FILTER = (
    filters.TEXT
    & ~filters.COMMAND
    & ~filters.Regex(_MENU_PATTERN)
)


def _clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(DRAFT_KEY, None)
    context.user_data.pop(PAYMENT_KEY, None)


def _draft(context: ContextTypes.DEFAULT_TYPE) -> NaturalExpenseDraft:
    draft = context.user_data.get(DRAFT_KEY)
    if not isinstance(draft, NaturalExpenseDraft):
        raise RuntimeError("Rascunho de despesa ausente.")
    return draft


async def start_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear(context)
    message = update.effective_message
    if message is None:
        return ConversationHandler.END
    await message.reply_text(
        "Envie o gasto em uma linha.\n\n"
        "Exemplos:\n"
        "mercado 230,50\n"
        "tablet 1700 parcelado em 10x\n"
        "presente giron, 300, tomas, yuzo\n"
        "allianz 390 mensal dia 28",
        reply_markup=build_main_menu(),
    )
    return NATURAL_TEXT


async def receive_direct_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear(context)
    return await receive_natural_text(update, context)


async def receive_natural_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = update.effective_message
    if message is None:
        return NATURAL_TEXT
    try:
        draft = NaturalExpenseParser().parse(message.text or "")
    except NaturalExpenseParseError as error:
        await message.reply_text(
            f"Não consegui interpretar: {error}\n\n"
            "Tente algo como: mercado 230,50",
            reply_markup=build_main_menu(),
        )
        return NATURAL_TEXT

    context.user_data[DRAFT_KEY] = draft
    await message.reply_text(
        "Como você pagou?",
        reply_markup=build_payment_keyboard(),
    )
    return PAYMENT_METHOD


async def receive_payment_method(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = update.effective_message
    if message is None:
        return PAYMENT_METHOD
    payment = (message.text or "").strip()
    if payment not in PAYMENT_METHODS:
        await message.reply_text(
            "Escolha uma das quatro formas de pagamento.",
            reply_markup=build_payment_keyboard(),
        )
        return PAYMENT_METHOD

    draft = _draft(context)
    if draft.is_installment and payment != PAYMENT_CREDIT_CARD:
        await message.reply_text(
            "Compras parceladas devem usar Cartão de crédito.",
            reply_markup=build_payment_keyboard(),
        )
        return PAYMENT_METHOD

    context.user_data[PAYMENT_KEY] = payment
    await message.reply_text(
        _confirmation_text(draft, payment),
        reply_markup=build_confirmation_keyboard(),
    )
    return CONFIRM


async def confirm_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    message = update.effective_message
    if message is None:
        return CONFIRM
    if (message.text or "").strip() != BUTTON_CONFIRM:
        return await cancel_expense(update, context)

    draft = _draft(context)
    payment = str(context.user_data.get(PAYMENT_KEY, ""))

    try:
        with container_context() as container:
            category = container.lookup_service.get_category(draft.category)
            payment_entity = container.lookup_service.get_payment_method(payment)

            if draft.is_recurring:
                recurring = container.recurring_expense_service.create_recurring(
                    description=draft.description,
                    amount=draft.total,
                    category_id=category.id,
                    payment_method_id=payment_entity.id,
                    due_day=draft.recurring_due_day or date.today().day,
                    start_date=date.today(),
                )
                profile = container.financial_profile_repository.get_or_create_default()
                container.recurring_expense_service.materialize(
                    from_year=date.today().year,
                    from_month=date.today().month,
                    months=profile.projection_months,
                )
                result_text = (
                    f"Gasto recorrente salvo: {recurring.description} "
                    f"({format_brl(recurring.amount)} todo dia {recurring.due_day})."
                )
            else:
                profile = container.financial_profile_repository.get_or_create_default()
                credit = payment == PAYMENT_CREDIT_CARD
                due_date = None
                installment_count = draft.installments
                if credit:
                    due_date = first_installment_date(
                        purchase_date=date.today(),
                        closing_day=profile.credit_card_closing_day,
                        installment_day=profile.credit_card_installment_day,
                    )
                expense = container.expense_service.create_expense(
                    ExpenseCreate(
                        purchase_date=datetime.now(),
                        purchase_place=draft.description,
                        purchase_value=draft.total,
                        category=category.name,
                        payment_method=payment_entity.name,
                        is_installment=credit,
                        installments=installment_count if credit else 1,
                        first_installment_due_date=due_date,
                        is_shared=draft.is_shared,
                        shared_people=draft.shared_people,
                        owner_amount=draft.owner_amount,
                        notes=f"Registrada pelo Telegram: {draft.original_text}",
                    )
                )
                result_text = f"Gasto salvo com sucesso. ID #{expense.id}."
    except Exception as error:
        await message.reply_text(
            f"Não foi possível salvar: {error}",
            reply_markup=build_main_menu(),
        )
        _clear(context)
        return ConversationHandler.END

    _clear(context)
    await message.reply_text(result_text, reply_markup=build_main_menu())
    return ConversationHandler.END


async def cancel_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    _clear(context)
    message = update.effective_message
    if message is not None:
        await message.reply_text(
            "Cadastro cancelado.",
            reply_markup=build_main_menu(),
        )
    return ConversationHandler.END


def _confirmation_text(draft: NaturalExpenseDraft, payment: str) -> str:
    lines = [
        "Confira antes de salvar:",
        "",
        f"Descrição: {draft.description}",
        f"Valor total: {format_brl(draft.total)}",
        f"Categoria: {draft.category}",
        f"Pagamento: {payment}",
    ]
    if draft.is_installment:
        installment = (draft.total / Decimal(draft.installments)).quantize(Decimal("0.01"))
        lines.append(
            f"Parcelamento: {draft.installments}x de aproximadamente {format_brl(installment)}"
        )
    if draft.is_recurring:
        lines.append(f"Recorrência: todo dia {draft.recurring_due_day}")
    if draft.is_shared:
        split = SharedExpenseSplitter().split(
            total=draft.total,
            people=draft.shared_people,
            owner_amount=draft.owner_amount,
        )
        lines.append("")
        lines.append(f"Sua parte: {format_brl(split.owner_amount)}")
        for item in split.allocations:
            lines.append(f"{item.person_name}: {format_brl(item.amount)}")
    lines.extend(["", "Confirmar?"])
    return "\n".join(lines)


def build_expense_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("gasto", start_expense),
            MessageHandler(filters.Regex(f"^{re.escape(MENU_ADD_EXPENSE)}$"), start_expense),
            MessageHandler(DIRECT_TEXT_FILTER, receive_direct_text),
        ],
        states={
            NATURAL_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_natural_text)],
            PAYMENT_METHOD: [
                MessageHandler(filters.Regex("^(?:" + "|".join(re.escape(v) for v in PAYMENT_METHODS) + ")$"), receive_payment_method),
            ],
            CONFIRM: [
                MessageHandler(filters.Regex(f"^{re.escape(BUTTON_CONFIRM)}$"), confirm_expense),
                MessageHandler(filters.Regex(f"^{re.escape(BUTTON_CANCEL)}$"), cancel_expense),
            ],
        },
        fallbacks=[
            CommandHandler("cancelar", cancel_expense),
            MessageHandler(filters.Regex(f"^{re.escape(BUTTON_CANCEL)}$"), cancel_expense),
        ],
        allow_reentry=True,
        per_chat=True,
        per_user=True,
    )
