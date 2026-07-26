from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.api.dependencies import get_container
from app.api.schemas.receivable import (
    ReceivableDetailResponse,
    ReceivableHistoryResponse,
    ReceivableItemResponse,
    ReceivablePersonSummaryResponse,
    ReceivableSettlementResponse,
    ReceivableSummaryResponse,
    SettledReceivableItemResponse,
)
from app.container import Container


router = APIRouter(
    prefix="/receivables",
    tags=["receivables"],
)


@router.get(
    "",
    response_model=ReceivableSummaryResponse,
)
def list_receivables(
    container: Container = Depends(
        get_container
    ),
) -> ReceivableSummaryResponse:
    rows = (
        container.receivable_service
        .list_open_summary()
    )

    people = [
        ReceivablePersonSummaryResponse(
            person_id=row.person_id,
            person_name=row.person_name,
            total=row.total,
            pending_count=row.pending_count,
        )
        for row in rows
    ]

    total_general = sum(
        (
            person.total
            for person in people
        ),
        start=Decimal("0.00"),
    )

    return ReceivableSummaryResponse(
        people=people,
        total_general=total_general,
    )


@router.get(
    "/settled",
    response_model=ReceivableHistoryResponse,
)
def list_settled_receivables(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    container: Container = Depends(
        get_container
    ),
) -> ReceivableHistoryResponse:
    rows = (
        container.receivable_service
        .list_recent_settled(limit=limit)
    )

    return ReceivableHistoryResponse(
        items=[
            SettledReceivableItemResponse(
                receivable_id=row.receivable_id,
                expense_id=row.expense_id,
                person_id=row.person_id,
                person_name=row.person_name,
                purchase_place=row.purchase_place,
                purchase_date=row.purchase_date,
                amount=row.amount,
                settled_at=row.settled_at,
            )
            for row in rows
        ]
    )


@router.get(
    "/people/{person_id}",
    response_model=ReceivableDetailResponse,
)
def list_person_receivables(
    person_id: int,
    container: Container = Depends(
        get_container
    ),
) -> ReceivableDetailResponse:
    rows = (
        container.receivable_service
        .list_open_for_person_id(
            person_id
        )
    )

    items = [
        ReceivableItemResponse(
            receivable_id=row.receivable_id,
            expense_id=row.expense_id,
            person_id=row.person_id,
            person_name=row.person_name,
            purchase_place=row.purchase_place,
            purchase_date=row.purchase_date,
            amount=row.amount,
        )
        for row in rows
    ]

    person_name = (
        items[0].person_name
        if items
        else ""
    )

    total = sum(
        (
            item.amount
            for item in items
        ),
        start=Decimal("0.00"),
    )

    return ReceivableDetailResponse(
        person_id=person_id,
        person_name=person_name,
        items=items,
        total=total,
    )


@router.post(
    "/{receivable_id}/settle",
    response_model=(
        ReceivableSettlementResponse
    ),
)
def settle_receivable(
    receivable_id: int,
    container: Container = Depends(
        get_container
    ),
) -> ReceivableSettlementResponse:
    receivable = (
        container.receivable_service
        .settle(receivable_id)
    )

    return ReceivableSettlementResponse(
        receivable_id=receivable.id,
        is_settled=receivable.is_settled,
        settled_at=receivable.settled_at,
    )


@router.post(
    "/{receivable_id}/reopen",
    response_model=(
        ReceivableSettlementResponse
    ),
)
def reopen_receivable(
    receivable_id: int,
    container: Container = Depends(
        get_container
    ),
) -> ReceivableSettlementResponse:
    receivable = (
        container.receivable_service
        .reopen(receivable_id)
    )

    return ReceivableSettlementResponse(
        receivable_id=receivable.id,
        is_settled=receivable.is_settled,
        settled_at=receivable.settled_at,
    )
