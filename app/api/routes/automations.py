import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.api.dependencies import (
    get_container,
)
from app.api.schemas.automation import (
    AutomationDeliveryResponse,
    AutomationHistoryResponse,
    AutomationMessageResponse,
    AutomationPreviewResponse,
    AutomationRunResponse,
    AutomationSettingsRequest,
    AutomationSettingsResponse,
)
from app.container import Container
from app.notifications import (
    TelegramNotifier,
)
from app.services.automation_service import (
    AutomationEvent,
    AutomationSettingsView,
)


router = APIRouter(
    prefix="/automations",
    tags=["automations"],
)


def serialize_settings(
    settings: AutomationSettingsView,
) -> AutomationSettingsResponse:
    return AutomationSettingsResponse(
        enabled=settings.enabled,
        telegram_connected=(
            settings.telegram_connected
        ),
        timezone=settings.timezone,
        daily_summary_enabled=(
            settings.daily_summary_enabled
        ),
        daily_summary_hour=(
            settings.daily_summary_hour
        ),
        weekly_summary_enabled=(
            settings.weekly_summary_enabled
        ),
        weekly_summary_weekday=(
            settings
            .weekly_summary_weekday
        ),
        weekly_summary_hour=(
            settings.weekly_summary_hour
        ),
        installment_reminders_enabled=(
            settings
            .installment_reminders_enabled
        ),
        installment_reminder_days=(
            settings
            .installment_reminder_days
        ),
        reminder_hour=(
            settings.reminder_hour
        ),
        budget_alerts_enabled=(
            settings
            .budget_alerts_enabled
        ),
        budget_alert_threshold=(
            settings
            .budget_alert_threshold
        ),
    )


def serialize_event(
    event: AutomationEvent,
) -> AutomationMessageResponse:
    return AutomationMessageResponse(
        kind=event.kind,
        title=event.title,
        message=event.message,
        scheduled_for=(
            event.scheduled_for
        ),
    )


@router.get(
    "/settings",
    response_model=(
        AutomationSettingsResponse
    ),
)
def get_settings(
    container: Container = Depends(
        get_container
    ),
) -> AutomationSettingsResponse:
    return serialize_settings(
        container.automation_service
        .get_settings()
    )


@router.put(
    "/settings",
    response_model=(
        AutomationSettingsResponse
    ),
)
def save_settings(
    payload: AutomationSettingsRequest,
    container: Container = Depends(
        get_container
    ),
) -> AutomationSettingsResponse:
    try:
        settings = (
            container.automation_service
            .save_settings(
                **payload.model_dump()
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return serialize_settings(
        settings
    )


@router.post(
    "/disconnect",
    response_model=(
        AutomationSettingsResponse
    ),
)
def disconnect_telegram(
    container: Container = Depends(
        get_container
    ),
) -> AutomationSettingsResponse:
    return serialize_settings(
        container.automation_service
        .disconnect_telegram()
    )


@router.get(
    "/preview",
    response_model=(
        AutomationPreviewResponse
    ),
)
def preview(
    container: Container = Depends(
        get_container
    ),
) -> AutomationPreviewResponse:
    events = (
        container.automation_service
        .preview()
    )

    return AutomationPreviewResponse(
        items=[
            serialize_event(event)
            for event in events
        ]
    )


@router.post(
    "/run",
    response_model=AutomationRunResponse,
)
async def run_now(
    container: Container = Depends(
        get_container
    ),
) -> AutomationRunResponse:
    token = os.getenv(
        "TELEGRAM_TOKEN",
        "",
    )

    try:
        result = await (
            container.automation_service
            .run_due(
                sender=TelegramNotifier(
                    token
                ),
                force=True,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return AutomationRunResponse(
        generated=result.generated,
        sent=result.sent,
        skipped=result.skipped,
        failed=result.failed,
        items=[
            serialize_event(event)
            for event in result.events
        ],
    )


@router.get(
    "/deliveries",
    response_model=(
        AutomationHistoryResponse
    ),
)
def list_deliveries(
    limit: int = Query(
        default=30,
        ge=1,
        le=100,
    ),
    container: Container = Depends(
        get_container
    ),
) -> AutomationHistoryResponse:
    items = (
        container.automation_service
        .list_deliveries(limit=limit)
    )

    return AutomationHistoryResponse(
        items=[
            AutomationDeliveryResponse(
                id=item.id,
                kind=item.kind,
                status=item.status,
                message=item.message,
                scheduled_for=(
                    item.scheduled_for
                ),
                sent_at=item.sent_at,
                error_message=(
                    item.error_message
                ),
                created_at=item.created_at,
            )
            for item in items
        ]
    )
