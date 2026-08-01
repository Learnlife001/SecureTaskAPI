import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.config import settings


class SlidingWindowRateLimiter:
    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.requests:
                retry_after = max(1, int(self.window_seconds - (now - events[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts",
                    headers={"Retry-After": str(retry_after)},
                )
            events.append(now)


auth_limiter = SlidingWindowRateLimiter(
    settings.AUTH_RATE_LIMIT_REQUESTS,
    settings.AUTH_RATE_LIMIT_WINDOW_SECONDS,
)


def enforce_auth_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    auth_limiter.check(f"{client_host}:{request.url.path}")
