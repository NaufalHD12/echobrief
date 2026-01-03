import time

import redis.asyncio as redis

from .config import settings


class RedisRateLimiter:
    """Redis-based rate limiter using sliding window algorithm"""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is allowed under rate limit

        Args:
            key: Unique identifier (e.g., IP address or user ID)
            limit: Maximum requests allowed in the window
            window: Time window in seconds (default: 60)

        Returns:
            True if allowed, False if limit exceeded
        """
        current_time = int(time.time())
        window_start = current_time - window

        # Use Redis sorted set to track requests in sliding window
        # Score is timestamp, member is unique request ID
        request_id = f"{key}:{current_time}:{id(self)}"

        # Add current request to the set
        await self.redis.zadd(key, {request_id: current_time})

        # Remove old requests outside the window
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        count = await self.redis.zcount(key, window_start, current_time)

        # Set expiration on the key to auto-cleanup
        await self.redis.expire(key, window * 2)

        return count <= limit

    async def get_remaining_requests(
        self, key: str, limit: int, window: int = 60
    ) -> int:
        """
        Get remaining requests allowed in current window

        Args:
            key: Unique identifier
            limit: Rate limit
            window: Time window in seconds

        Returns:
            Number of remaining requests
        """
        current_time = int(time.time())
        window_start = current_time - window

        # Clean old requests
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count current requests
        count = await self.redis.zcount(key, window_start, current_time)

        remaining = max(0, limit - count)
        return remaining

    async def get_reset_time(self, key: str, window: int = 60) -> int:
        """
        Get time until rate limit resets (next window)

        Args:
            key: Unique identifier
            window: Time window in seconds

        Returns:
            Seconds until reset
        """
        current_time = int(time.time())
        window_start = current_time - window

        # Get oldest request in current window
        oldest_requests = await self.redis.zrangebyscore(
            key, window_start, current_time, withscores=True, start=0, num=1
        )

        if oldest_requests:
            oldest_time = int(oldest_requests[0][1])
            reset_time = (oldest_time + window) - current_time
            return max(0, reset_time)

        return window
