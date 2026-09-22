from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subscription_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider_payment_id: str
    paid_at: datetime | None
    created_at: datetime
