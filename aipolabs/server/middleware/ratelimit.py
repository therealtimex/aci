import json

from limits import RateLimitItem, RateLimitItemPerDay, RateLimitItemPerSecond
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from aipolabs.common.logging import get_logger
from aipolabs.server.config import RATE_LIMIT_IP_PER_DAY, RATE_LIMIT_IP_PER_SECOND

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.storage = MemoryStorage()
        self.limiter = MovingWindowRateLimiter(self.storage)
        self.rate_limits: dict[str, RateLimitItem] = {
            "ip-per-second": RateLimitItemPerSecond(amount=RATE_LIMIT_IP_PER_SECOND),
            "ip-per-day": RateLimitItemPerDay(amount=RATE_LIMIT_IP_PER_DAY),
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Determine the rate limit key based on authentication method
        rate_limit_key = self._get_rate_limit_key(request)
        for rate_limit_name, rate_limit in self.rate_limits.items():
            if not await self.limiter.hit(rate_limit, rate_limit_key):
                return Response(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=json.dumps({"detail": f"Rate limit exceeded: {rate_limit_name}"}),
                    headers=await self._get_rate_limit_headers(rate_limit_key),
                )

        response = await call_next(request)

        # Add rate limit headers for all limits
        headers = await self._get_rate_limit_headers(rate_limit_key)
        response.headers.update(headers)

        return response

    # TODO: only do ip based rate limiting in middleware
    # consider api key based rate limiting in dependencies where api key is validated
    def _get_rate_limit_key(self, request: Request) -> str:
        # TODO: client.host should always be set correctly because of ProxyHeadersMiddleware?
        # (remove logs)
        logger.warning(f"request.client: {request.client}")
        if request.client and request.client.host:
            return f"ip:{request.client.host}"
        else:
            logger.error("request.client.host not set")
            return "ip:127.0.0.1"

    async def _get_rate_limit_headers(self, key: str) -> dict:
        headers = {}
        for rate_limit_name, rate_limit in self.rate_limits.items():
            window_stats = await self.limiter.get_window_stats(rate_limit, key)
            current_usage = window_stats[1]
            reset_time = window_stats[0]

            headers[f"X-RateLimit-Limit-{rate_limit_name}"] = str(rate_limit.amount)
            headers[f"X-RateLimit-Remaining-{rate_limit_name}"] = str(
                max(0, rate_limit.amount - current_usage)
            )
            headers[f"X-RateLimit-Reset-{rate_limit_name}"] = str(reset_time)
        return headers
