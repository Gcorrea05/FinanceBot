from fastapi import (
    APIRouter,
    Depends,
)

from app.api.dependencies import get_container
from app.api.schemas.reference import (
    ReferenceItemResponse,
    ReferenceListResponse,
)
from app.container import Container


router = APIRouter(
    prefix="/references",
    tags=["references"],
)


@router.get(
    "/categories",
    response_model=ReferenceListResponse,
)
def list_categories(
    container: Container = Depends(
        get_container
    ),
) -> ReferenceListResponse:
    names = (
        container.lookup_service
        .list_category_names()
    )

    return ReferenceListResponse(
        items=[
            ReferenceItemResponse(
                name=name
            )
            for name in names
        ]
    )


@router.get(
    "/payment-methods",
    response_model=ReferenceListResponse,
)
def list_payment_methods(
    container: Container = Depends(
        get_container
    ),
) -> ReferenceListResponse:
    names = (
        container.lookup_service
        .list_payment_method_names()
    )

    return ReferenceListResponse(
        items=[
            ReferenceItemResponse(
                name=name
            )
            for name in names
        ]
    )
