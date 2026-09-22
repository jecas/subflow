from fastapi import APIRouter

from app.api.dependencies import DbSession
from app.schemas.webhook import (
    PaymentWebhook,
    WebhookResponse,
)
from app.services.webhook import WebhookService


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post(
    "/payments",
    response_model=WebhookResponse,
)
async def payment_webhook(
    data: PaymentWebhook,
    session: DbSession,
) -> WebhookResponse:
    return await WebhookService(
        session
    ).process_payment_event(data)
