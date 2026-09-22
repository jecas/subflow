from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        customer_id: UUID,
    ) -> Customer | None:
        return await self.session.get(Customer, customer_id)

    async def get_by_email(
        self,
        email: str,
    ) -> Customer | None:
        result = await self.session.execute(
            select(Customer).where(
                Customer.email == email.lower()
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Customer]:
        result = await self.session.execute(
            select(Customer).order_by(
                Customer.created_at.desc()
            )
        )
        return list(result.scalars().all())

    def add(self, customer: Customer) -> None:
        self.session.add(customer)
