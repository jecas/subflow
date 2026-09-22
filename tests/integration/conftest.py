import pytest_asyncio
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import engine


@pytest_asyncio.fixture(
    autouse=True,
)
async def clean_test_state():
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE "
                "webhook_events, payments, "
                "subscriptions, customers, plans "
                "RESTART IDENTITY CASCADE"
            )
        )

    await redis_client.flushdb()

    yield

    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE "
                "webhook_events, payments, "
                "subscriptions, customers, plans "
                "RESTART IDENTITY CASCADE"
            )
        )

    await redis_client.flushdb()
