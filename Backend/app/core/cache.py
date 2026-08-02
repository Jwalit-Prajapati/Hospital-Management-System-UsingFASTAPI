import json
from typing import Callable
import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self,app, redis_url: str = settings.REDIS_URL, ttl: int = 180):
        super().__init__(app)
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method != "GET":
            return await call_next(request)

        if request.url.path in ["/health","/docs","/openapi.json","/redoc"]:
            return await call_next(request)

        cache_key = f"cache:{request.url.path}:{request.query_params}"

        cached_response = await self.redis_client.get(cache_key)

        if cached_response:
            cached_data = json.loads(cached_response)
            return Response(
                content = cached_data["content"],
                status_code = cached_data["status_code"],
                headers = cached_data["headers"],
                media_type = cached_data["media_type"]
            )

        response = await call_next(request)

        if 200<= response.status_code < 300:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            cached_data = {
                "content" : response_body.decode(),
                "status_code" : response.status_code,
                "headers" : dict(response.headers),
                "media_type" : response.media_type
            }

            await self.redis_client.setex(cache_key, self.ttl, json.dumps(cached_data))

            return Response(
                content = response_body,
                status_code = response.status_code,
                headers = dict(response.headers),
                media_type = response.media_type
            )
        
        return response

        
