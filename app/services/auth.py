from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.customers = CustomerRepository(session)

    async def register(
        self,
        data: RegisterRequest,
    ) -> Customer:
        existing = await self.customers.get_by_email(
            data.email
        )

        if existing:
            raise ConflictError(
                "A customer with this email already exists."
            )

        customer = Customer(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )

        self.customers.add(customer)

        await self.session.commit()
        await self.session.refresh(customer)

        return customer

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        customer = await self.customers.get_by_email(
            data.email
        )

        if (
            customer is None
            or not customer.is_active
            or not verify_password(
                data.password,
                customer.password_hash,
            )
        ):
            raise AuthenticationError(
                "Invalid email or password."
            )

        return TokenResponse(
            access_token=create_access_token(
                customer.id
            )
        )
