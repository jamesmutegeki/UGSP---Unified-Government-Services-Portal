import hashlib
import uuid
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class DPPAComplianceMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = hashlib.sha256(
            f"{uuid.uuid4()}|{time.time()}".encode()
        ).hexdigest()[:16]
        request.state.request_id = request_id
        request.state.start_time = time.time()

        response = await call_next(request)

        elapsed = time.time() - request.state.start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(round(elapsed * 1000, 1))

        user_nin = getattr(request.state, "user_nin", None)
        print(
            f"[DPPA AUDIT] {request_id} | {request.method} {request.url.path} "
            f"| {response.status_code} | {user_nin or 'anonymous'} | {elapsed:.3f}s"
        )
        return response


_RATE_WINDOW = 60
_RATE_LIMIT = 100
_rate_store: dict[str, list[float]] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        now = time.time()
        client_ip = request.client.host if request.client else "unknown"
        window = _rate_store.get(client_ip, [])
        window = [t for t in window if now - t < _RATE_WINDOW]
        if len(window) >= _RATE_LIMIT:
            return Response(status_code=429, content="Rate limit exceeded. Try again later.")
        window.append(now)
        _rate_store[client_ip] = window
        return await call_next(request)
