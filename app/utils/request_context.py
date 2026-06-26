import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.responses import Response

from app.core.request_context import request_id_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate and propagate a per-request ID for logs and client tracing.
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_context.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
