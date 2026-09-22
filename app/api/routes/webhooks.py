import secrets
from typing import Annotated

from fastapi import APIRouter, Header

from app.api.dependencies import DbSession
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.schemas.webhook import (
    PaymentWebhook,
    WebhookResponse,
)
from app.services.webhook import WebhookService

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)

settings = get_settings()


@router.post(
    "/payments",
    response_model=WebhookResponse,
)
async def payment_webhook(
    data: PaymentWebhook,
    session: DbSession,
    webhook_secret: Annotated[
        str | None,
        Header(alias="X-Webhook-Secret"),
    ] = None,
) -> WebhookResponse:
    if (
        webhook_secret is None
        or not secrets.compare_digest(
            webhook_secret,
            settings.payment_webhook_secret,
        )
    ):
        raise AuthenticationError(
            "Invalid webhook credentials."
        )

    return await WebhookService(
        session
    ).process_payment_event(data)
