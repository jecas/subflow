from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from app.models.plan import Plan
from app.repositories.plan import PlanRepository
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.plans = PlanRepository(session)

    async def list_active(self) -> list[Plan]:
        return await self.plans.list_active()

    async def get(self, plan_id: UUID) -> Plan:
        plan = await self.plans.get(plan_id)

        if plan is None:
            raise NotFoundError("Plan not found.")

        return plan

    async def create(
        self,
        data: PlanCreate,
    ) -> Plan:
        existing = await self.plans.get_by_name(
            data.name
        )

        if existing:
            raise ConflictError(
                "A plan with this name already exists."
            )

        plan = Plan(**data.model_dump())

        self.plans.add(plan)

        await self.session.commit()
        await self.session.refresh(plan)

        return plan

    async def update(
        self,
        plan_id: UUID,
        data: PlanUpdate,
    ) -> Plan:
        plan = await self.get(plan_id)

        for field, value in data.model_dump(
            exclude_unset=True
        ).items():
            setattr(plan, field, value)

        await self.session.commit()
        await self.session.refresh(plan)

        return plan
