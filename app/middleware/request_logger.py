from __future__ import annotations

import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import LOGGER_NAME
import logging


logger = logging.getLogger(LOGGER_NAME)


def _mask_client_host(host: str | None) -> str:
    if not host:
        return "unknown"
    if "." in host:
        octets = host.split(".")
        if len(octets) == 4:
            return ".".join([octets[0], octets[1], "x", "x"])
    return host


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid4())
        start_time = time.perf_counter()
        client_host = _mask_client_host(request.client.host if request.client else None)
        route_path = request.url.path

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "request_failed request_id=%s method=%s path=%s client=%s duration_ms=%s",
                request_id,
                request.method,
                route_path,
                client_host,
                duration_ms,
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed request_id=%s method=%s path=%s status_code=%s client=%s duration_ms=%s",
            request_id,
            request.method,
            route_path,
            response.status_code,
            client_host,
            duration_ms,
        )
        return response
