from fastapi import APIRouter, status

from app.api.dependencies import DbSession
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.customer import CustomerResponse
from app.services.auth import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    session: DbSession,
) -> CustomerResponse:
    return await AuthService(session).register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: DbSession,
) -> TokenResponse:
    return await AuthService(session).login(data)
