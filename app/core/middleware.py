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


def verify_token_dependency(token: str) -> dict | None:
    if not token or not token.startswith("ugpass_"):
        return None
    parts = token.replace("ugpass_", "", 1).split("_", 1)
    if len(parts) < 1 or len(parts[0]) < 10:
        return None
    return {
        "nin": parts[0],
        "name": f"Citizen {parts[0][:4]}",
        "email": f"{parts[0]}@ugpass.go.ug",
    }
