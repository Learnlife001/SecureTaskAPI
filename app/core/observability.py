import logging
import threading
import time
import uuid
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("securetask.http")
_lock = threading.Lock()
_request_counts: dict[tuple[str, str, int], int] = defaultdict(int)
_request_duration_sum: dict[tuple[str, str], float] = defaultdict(float)
_request_duration_count: dict[tuple[str, str], int] = defaultdict(int)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        started = time.perf_counter()
        status_code = 500
        response = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - started
            route = request.scope.get("route")
            path = getattr(route, "path", request.url.path)
            with _lock:
                _request_counts[(request.method, path, status_code)] += 1
                _request_duration_sum[(request.method, path)] += duration
                _request_duration_count[(request.method, path)] += 1
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
            if response is not None:
                response.headers["X-Request-ID"] = request_id


def metrics_response() -> Response:
    lines = [
        "# HELP securetask_http_requests_total Total HTTP requests.",
        "# TYPE securetask_http_requests_total counter",
    ]
    with _lock:
        for (method, path, status), value in sorted(_request_counts.items()):
            lines.append(
                f'securetask_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {value}'
            )
        lines.extend(
            [
                "# HELP securetask_http_request_duration_seconds HTTP request duration.",
                "# TYPE securetask_http_request_duration_seconds summary",
            ]
        )
        for (method, path), value in sorted(_request_duration_sum.items()):
            labels = f'method="{method}",path="{path}"'
            lines.append(
                f"securetask_http_request_duration_seconds_sum{{{labels}}} {value}"
            )
            lines.append(
                f"securetask_http_request_duration_seconds_count{{{labels}}} {_request_duration_count[(method, path)]}"
            )
    return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
