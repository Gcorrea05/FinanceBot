import asyncio
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.expense_input import (
    ExpenseInputError,
    parse_shared_person_entry,
)
from app.bot.handlers.expense_conversation import (
    CURRENT_STATE_KEY,
    DRAFT_KEY,
    HISTORY_KEY,
    NOTES,
    SHARED_PEOPLE,
    receive_shared_people,
)
from app.bot.keyboards.expense import (
    BUTTON_FINISH_PEOPLE,
)


def make_update(text: str):
    message = SimpleNamespace(
        text=text,
        reply_text=AsyncMock(),
    )

    return SimpleNamespace(
        effective_message=message,
    )


def make_context(
    shared_mode: str,
):
    return SimpleNamespace(
        user_data={
            DRAFT_KEY: {
                "purchase_value": Decimal(
                    "300.00"
                ),
                "shared_mode": shared_mode,
                "shared_people": [],
            },
            CURRENT_STATE_KEY: SHARED_PEOPLE,
            HISTORY_KEY: [],
        }
    )


def test_parse_one_equal_person():
    person = parse_shared_person_entry(
        "Tomas",
        shared_mode="equal",
    )

    assert person.name == "Tomas"
    assert person.amount is None


def test_parse_one_exact_person():
    person = parse_shared_person_entry(
        "Tomas=70,00",
        shared_mode="exact",
    )

    assert person.name == "Tomas"
    assert person.amount == Decimal("70.00")


def test_reject_multiple_people_in_one_response():
    try:
        parse_shared_person_entry(
            "Sofia, Tomas",
            shared_mode="equal",
        )

    except ExpenseInputError:
        pass

    else:
        raise AssertionError(
            "Expected ExpenseInputError."
        )


def test_equal_people_are_added_in_loop():
    context = make_context("equal")

    first_state = asyncio.run(
        receive_shared_people(
            make_update("Sofia"),
            context,
        )
    )

    second_state = asyncio.run(
        receive_shared_people(
            make_update("Tomas"),
            context,
        )
    )

    people = context.user_data[
        DRAFT_KEY
    ]["shared_people"]

    assert first_state == SHARED_PEOPLE
    assert second_state == SHARED_PEOPLE
    assert [
        person.name
        for person in people
    ] == [
        "Sofia",
        "Tomas",
    ]


def test_duplicate_person_is_not_added():
    context = make_context("equal")

    asyncio.run(
        receive_shared_people(
            make_update("Tomas"),
            context,
        )
    )

    state = asyncio.run(
        receive_shared_people(
            make_update("TOMAS"),
            context,
        )
    )

    people = context.user_data[
        DRAFT_KEY
    ]["shared_people"]

    assert state == SHARED_PEOPLE
    assert len(people) == 1


def test_finish_people_moves_to_notes():
    context = make_context("exact")

    asyncio.run(
        receive_shared_people(
            make_update("Tomas=70"),
            context,
        )
    )

    state = asyncio.run(
        receive_shared_people(
            make_update(
                BUTTON_FINISH_PEOPLE
            ),
            context,
        )
    )

    assert state == NOTES
