from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


class PlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        plan_id: UUID,
    ) -> Plan | None:
        return await self.session.get(Plan, plan_id)

    async def get_by_name(
        self,
        name: str,
    ) -> Plan | None:
        result = await self.session.execute(
            select(Plan).where(Plan.name == name)
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> list[Plan]:
        result = await self.session.execute(
            select(Plan)
            .where(Plan.is_active.is_(True))
            .order_by(Plan.price)
        )
        return list(result.scalars().all())

    def add(self, plan: Plan) -> None:
        self.session.add(plan)
