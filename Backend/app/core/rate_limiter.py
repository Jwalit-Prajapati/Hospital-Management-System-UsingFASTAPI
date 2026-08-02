from typing import Callable
import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from app.core.config import settings

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str = settings.REDIS_URL, rate_limit: int = 60):
        super().__init__(app)
        self.redis_client = redis.from_url(redis_url)
        self.rate_limit = rate_limit
        self.window = 60

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in["/health","/docs","/openapi.json","/redoc"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"

        key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            current = await self.redis_client.get(key)
            current = int(current) if current else 0

            if current >= self.rate_limit:
                return Response(
                    content="Rate limit exceeded. Try again later.",
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(self.window)},
                )

            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window)
            await pipe.execute()
        except redis.ConnectionError:
            pass
        except Exception as e:
            print(f"Rate Limiter error: {e}")

        return await call_next(request)
