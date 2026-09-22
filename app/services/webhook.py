import json
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import PaymentStatus
from app.models.webhook_event import WebhookEvent
from app.repositories.payment import PaymentRepository
from app.repositories.webhook_event import WebhookEventRepository
from app.schemas.webhook import PaymentWebhook, WebhookResponse


class WebhookService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.events = WebhookEventRepository(session)
        self.payments = PaymentRepository(session)

    async def process_payment_event(self, data: PaymentWebhook) -> WebhookResponse:
        existing = await self.events.get_by_provider_event_id(data.event_id)
        if existing is not None:
            return WebhookResponse(
                event_id=data.event_id,
                processed=existing.processed_at is not None,
                duplicate=True,
            )

        event = WebhookEvent(
            provider_event_id=data.event_id,
            event_type=data.event_type,
            payload=json.dumps(data.model_dump(mode="json")),
        )
        self.events.add(event)

        payment = await self.payments.get_by_provider_id(data.payment_id)
        if payment is not None:
            if data.event_type == "payment.succeeded":
                payment.status = PaymentStatus.SUCCEEDED
                payment.paid_at = datetime.now(UTC)
            elif data.event_type == "payment.failed":
                payment.status = PaymentStatus.FAILED

        event.processed_at = datetime.now(UTC)
        await self.session.commit()

        return WebhookResponse(
            event_id=data.event_id,
            processed=True,
            duplicate=False,
        )
