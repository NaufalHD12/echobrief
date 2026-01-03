import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .rate_limiter import RedisRateLimiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests"""

    def __init__(self, app: Callable):
        super().__init__(app)
        self.rate_limiter = RedisRateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for admin endpoints
        if request.url.path.startswith("/api/v1/admin/"):
            return await call_next(request)

        # Skip rate limiting for health checks and static files
        if (
            request.url.path.startswith("/health")
            or request.url.path.startswith("/audio/")
            or request.url.path.startswith("/avatars/")
            or request.url.path == "/"
        ):
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Determine rate limit based on endpoint
        if request.url.path.startswith("/api/v1/auth/"):
            # Stricter limit for auth endpoints
            limit = 25
            window = 60  # 1 minute
        else:
            # General API limit
            limit = 100
            window = 60  # 1 minute

        # Create unique key for rate limiting
        rate_limit_key = f"ratelimit:{client_ip}:{request.method}:{request.url.path}"

        # Check if request is allowed
        is_allowed = await self.rate_limiter.is_allowed(rate_limit_key, limit, window)

        if not is_allowed:
            # Get reset time for response headers
            reset_time = await self.rate_limiter.get_reset_time(rate_limit_key, window)

            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.method} {request.url.path}"
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "type": "rate_limit_exceeded",
                    "retry_after": reset_time,
                },
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                },
            )

        # Add rate limit headers to successful response
        response = await call_next(request)

        # Get remaining requests for headers
        remaining = await self.rate_limiter.get_remaining_requests(
            rate_limit_key, limit, window
        )
        reset_time = await self.rate_limiter.get_reset_time(rate_limit_key, window)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request

        Checks X-Forwarded-For header first (for proxy/load balancer),
        falls back to direct client IP.
        """
        # Check for forwarded IP (common with proxies/load balancers)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take first IP if multiple
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header (nginx)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client
        client_host = request.client.host if request.client else "unknown"
        return client_host
