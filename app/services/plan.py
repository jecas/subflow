from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.plan import PlanCache
from app.core.exceptions import NotFoundError
from app.models.plan import Plan
from app.repositories.plan import PlanRepository
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate


class PlanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PlanRepository(session)
        self.cache = PlanCache()

    async def list_active(
        self,
    ) -> list[PlanResponse]:
        cached = await self.cache.get()

        if cached is not None:
            return [
                PlanResponse.model_validate(plan)
                for plan in cached
            ]

        plans = await self.repository.list_active()

        responses = [
            PlanResponse.model_validate(plan)
            for plan in plans
        ]

        await self.cache.set(
            [
                response.model_dump(
                    mode="json"
                )
                for response in responses
            ]
        )

        return responses

    async def get(
        self,
        plan_id: UUID,
    ) -> Plan:
        plan = await self.repository.get(plan_id)

        if plan is None or not plan.is_active:
            raise NotFoundError(
                "Active plan not found."
            )

        return plan

    async def create(
        self,
        data: PlanCreate,
    ) -> Plan:
        plan = Plan(
            **data.model_dump()
        )

        self.repository.add(plan)

        await self.session.commit()
        await self.session.refresh(plan)

        await self.cache.invalidate()

        return plan

    async def update(
        self,
        plan_id: UUID,
        data: PlanUpdate,
    ) -> Plan:
        plan = await self.repository.get(plan_id)

        if plan is None:
            raise NotFoundError(
                "Plan not found."
            )

        updates = data.model_dump(
            exclude_unset=True
        )

        for field, value in updates.items():
            setattr(plan, field, value)

        await self.session.commit()
        await self.session.refresh(plan)

        await self.cache.invalidate()

        return plan
