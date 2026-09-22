from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import DbSession
from app.schemas.plan import PlanResponse
from app.services.plan import PlanService


router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)


@router.get(
    "",
    response_model=list[PlanResponse],
)
async def list_plans(
    session: DbSession,
) -> list[PlanResponse]:
    return await PlanService(
        session
    ).list_active()


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
)
async def get_plan(
    plan_id: UUID,
    session: DbSession,
) -> PlanResponse:
    return await PlanService(session).get(plan_id)
