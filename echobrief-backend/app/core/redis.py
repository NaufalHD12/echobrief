import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio.client import Redis

from .config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    _instance: Optional["RedisClient"] = None
    client: Optional[Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error key={key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Set value in Redis with TTL"""
        if not self.client:
            return False
        try:
            return await self.client.set(key, value, ex=ttl)  # type: ignore
        except Exception as e:
            logger.error(f"Redis set error key={key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error key={key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.client:
            return 0
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
                logger.debug(f"Deleted {len(keys)} keys matching {pattern}")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Redis delete_pattern error pattern={pattern}: {e}")
            return 0


redis_client = RedisClient()
