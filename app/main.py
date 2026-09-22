from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import admin, auth, customers, health, plans, subscriptions
from app.core.config import get_settings
from app.core.exceptions import SubFlowError
from app.core.redis import close_redis

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    version=settings.app_version,
    description=(
        "Subscription management API for customers, "
        "plans and recurring subscriptions."
    ),
)

app.include_router(health.router)

app.include_router(
    auth.router,
    prefix=settings.api_prefix,
)

app.include_router(
    customers.router,
    prefix=settings.api_prefix,
)

app.include_router(
    plans.router,
    prefix=settings.api_prefix,
)

app.include_router(
    subscriptions.router,
    prefix=settings.api_prefix,
)

app.include_router(
    admin.router,
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
