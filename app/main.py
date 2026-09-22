from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import (
    admin,
    auth,
    customers,
    health,
    plans,
    subscriptions,
    webhooks,
)
from app.core.config import get_settings
from app.core.exceptions import SubFlowError
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.redis import close_redis

settings = get_settings()

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    version=settings.app_version,
    description=(
        "Subscription management API for customers, "
        "plans, recurring subscriptions and payments."
    ),
)

app.add_middleware(
    RequestLoggingMiddleware
)

app.include_router(
    health.router
)

for router in (
    auth.router,
    customers.router,
    plans.router,
    subscriptions.router,
    admin.router,
    webhooks.router,
):
    app.include_router(
        router,
        prefix=settings.api_prefix,
    )


@app.exception_handler(SubFlowError)
async def subflow_error_handler(
    _: Request,
    exc: SubFlowError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
