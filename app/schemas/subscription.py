from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.subscription import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    plan_id: UUID


class SubscriptionChangePlan(BaseModel):
    plan_id: UUID


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    started_at: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
