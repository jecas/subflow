from typing import Any

from pydantic import BaseModel


class PaymentWebhook(BaseModel):
    event_id: str
    event_type: str
    payment_id: str
    data: dict[str, Any] = {}


class WebhookResponse(BaseModel):
    event_id: str
    processed: bool
    duplicate: bool
