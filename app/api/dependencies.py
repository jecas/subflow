from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.customer import Customer, CustomerRole
from app.repositories.customer import CustomerRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

DbSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


async def get_current_customer(
    session: DbSession,
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
) -> Customer:
    try:
        customer_id = decode_access_token(token)
    except (
        jwt.InvalidTokenError,
        ValueError,
        KeyError,
    ):
        raise AuthenticationError(
            "Invalid or expired access token."
        ) from None

    customer = await CustomerRepository(
        session
    ).get_by_id(customer_id)

    if customer is None or not customer.is_active:
        raise AuthenticationError(
            "Customer is not available."
        )

    return customer


async def require_admin(
    customer: Annotated[
        Customer,
        Depends(get_current_customer),
    ],
) -> Customer:
    if customer.role != CustomerRole.ADMIN:
        raise AuthorizationError(
            "Administrator access is required."
        )

    return customer


CurrentCustomer = Annotated[
    Customer,
    Depends(get_current_customer),
]

AdminCustomer = Annotated[
    Customer,
    Depends(require_admin),
]
