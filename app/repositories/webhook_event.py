from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_event import WebhookEvent


class WebhookEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, event: WebhookEvent) -> None:
        self.session.add(event)

    async def get_by_provider_event_id(self, provider_event_id: str) -> WebhookEvent | None:
        result = await self.session.execute(
            select(WebhookEvent).where(WebhookEvent.provider_event_id == provider_event_id)
        )
        return result.scalar_one_or_none()
