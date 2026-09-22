import json
import logging
from typing import Any

from redis.exceptions import RedisError

from app.core.config import get_settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

PLANS_CACHE_KEY = "plans:active"


class PlanCache:
    def __init__(self) -> None:
        self.redis = redis_client
        self.settings = get_settings()

    async def get(self) -> list[dict[str, Any]] | None:
        try:
            cached = await self.redis.get(
                PLANS_CACHE_KEY
            )
        except RedisError:
            logger.warning(
                "Redis unavailable while reading plans cache.",
                exc_info=True,
            )
            return None

        if cached is None:
            return None

        try:
            data = json.loads(cached)
        except json.JSONDecodeError:
            logger.warning(
                "Invalid JSON found in plans cache."
            )
            await self.invalidate()
            return None

        if not isinstance(data, list):
            logger.warning(
                "Unexpected data found in plans cache."
            )
            await self.invalidate()
            return None

        return data

    async def set(
        self,
        plans: list[dict[str, Any]],
    ) -> None:
        try:
            await self.redis.set(
                PLANS_CACHE_KEY,
                json.dumps(plans),
                ex=self.settings.plans_cache_ttl_seconds,
            )
        except RedisError:
            logger.warning(
                "Redis unavailable while writing plans cache.",
                exc_info=True,
            )

    async def invalidate(self) -> None:
        try:
            await self.redis.delete(
                PLANS_CACHE_KEY
            )
        except RedisError:
            logger.warning(
                "Redis unavailable while invalidating plans cache.",
                exc_info=True,
            )
