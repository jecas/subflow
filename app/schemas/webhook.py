from typing import Any

from pydantic import BaseModel, Field


class PaymentWebhook(BaseModel):
    event_id: str
    event_type: str
    payment_id: str
    data: dict[str, Any] = Field(
        default_factory=dict
    )


class WebhookResponse(BaseModel):
    event_id: str
    processed: bool
    duplicate: bool
