import pytest_asyncio
from sqlalchemy import text

from app.db.session import engine


@pytest_asyncio.fixture(
    autouse=True,
)
async def clean_database():
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE "
                "subscriptions, customers, plans "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield

    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE "
                "subscriptions, customers, plans "
                "RESTART IDENTITY CASCADE"
            )
        )
